"""IMAP 拉取指定发件人 + 主题关键词的最新邮件（纯文本正文）。"""

from __future__ import annotations

import email
import imaplib
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from email.header import decode_header
from email.message import Message
from email.utils import parsedate_to_datetime

from config import Settings


@dataclass(frozen=True)
class WeeklyMail:
    keyword: str
    subject: str
    body_text: str
    date: datetime
    body_html: str | None = None


def _decode_mime_header(raw: str | None) -> str:
    if not raw:
        return ""
    parts: list[str] = []
    for frag, charset in decode_header(raw):
        if isinstance(frag, bytes):
            parts.append(frag.decode(charset or "utf-8", errors="replace"))
        else:
            parts.append(str(frag))
    return "".join(parts).strip()


def _decode_part(part: Message) -> str:
    payload = part.get_payload(decode=True)
    if not payload:
        return ""
    charset = part.get_content_charset() or "utf-8"
    return payload.decode(charset, errors="replace")


def _sanitize_email_html(html: str) -> str:
    html = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", "", html)
    html = re.sub(r"(?is)<!--.*?-->", "", html)
    m = re.search(r"(?is)<body[^>]*>(.*)</body>", html)
    if m:
        html = m.group(1)
    return html.strip()


def _message_bodies(msg: Message) -> tuple[str, str | None]:
    """返回 (纯文本, 可选 HTML)，优先保留邮件 HTML 供 CMS 粘贴。"""
    plain = ""
    html_raw = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_disposition() == "attachment":
                continue
            if part.get_content_type() == "text/plain" and not plain:
                plain = _decode_part(part).strip()
            elif part.get_content_type() == "text/html" and not html_raw:
                html_raw = _decode_part(part).strip()
    else:
        raw = _decode_part(msg).strip()
        if msg.get_content_type() == "text/html":
            html_raw = raw
        else:
            plain = raw
    html: str | None = _sanitize_email_html(html_raw) if html_raw else None
    if not plain and html:
        plain = _html_to_plain(html)
    if not plain and not html:
        return "", None
    return plain, html


def _message_body_text(msg: Message) -> str:
    plain, _ = _message_bodies(msg)
    return plain


def _html_to_plain(html: str) -> str:
    text = re.sub(r"(?is)<(script|style).*?>.*?</\1>", "", html)
    text = re.sub(r"(?i)<br\s*/?>", "\n", text)
    text = re.sub(r"(?i)</p>", "\n", text)
    text = re.sub(r"<[^>]+>", "", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def _parse_message_date(msg: Message) -> datetime:
    raw = msg.get("Date")
    if raw:
        try:
            dt = parsedate_to_datetime(raw)
            if dt.tzinfo is None:
                return dt.replace(tzinfo=timezone.utc)
            return dt
        except (TypeError, ValueError, IndexError):
            pass
    return datetime.min.replace(tzinfo=timezone.utc)


def _imap_search_uids(conn: imaplib.IMAP4_SSL, sender: str) -> list[bytes]:
    # 部分服务器对中文 SEARCH 支持差，主题过滤在本地完成
    status, data = conn.uid("search", None, "FROM", f'"{sender}"')
    if status != "OK" or not data or not data[0]:
        return []
    return data[0].split()


def fetch_latest_by_keywords(settings: Settings, keywords: tuple[str, ...]) -> list[WeeklyMail]:
    try:
        conn = imaplib.IMAP4_SSL(settings.imap_host, settings.imap_port)
    except OSError as exc:
        raise RuntimeError(
            f"无法连接 IMAP {settings.imap_host}:{settings.imap_port}（{exc}）。"
            "Foxmail 若显示 995 多为 POP3，IMAP 请试 993。"
        ) from exc
    try:
        conn.login(settings.email_user, settings.email_password)
        status, _ = conn.select("INBOX")
        if status != "OK":
            raise RuntimeError(f"无法打开收件箱 INBOX: {status}")
        uids = _imap_search_uids(conn, settings.mail_sender)
        if not uids:
            raise RuntimeError(f"收件箱未找到来自 {settings.mail_sender} 的邮件")

        best: dict[str, WeeklyMail] = {}
        for uid in reversed(uids):
            status, data = conn.uid("fetch", uid, "(RFC822)")
            if status != "OK" or not data or not isinstance(data[0], tuple):
                continue
            msg = email.message_from_bytes(data[0][1])
            subject = _decode_mime_header(msg.get("Subject"))
            for kw in keywords:
                if kw in subject and kw not in best:
                    body_text, body_html = _message_bodies(msg)
                    if not body_text and not body_html:
                        raise RuntimeError(f"邮件「{subject}」无可用正文")
                    best[kw] = WeeklyMail(
                        keyword=kw,
                        subject=subject,
                        body_text=body_text,
                        body_html=body_html,
                        date=_parse_message_date(msg),
                    )
            if len(best) == len(keywords):
                break

        missing = [kw for kw in keywords if kw not in best]
        if missing:
            raise RuntimeError(f"未找到主题含以下关键词的最新邮件: {', '.join(missing)}")

        return [best[kw] for kw in keywords]
    finally:
        try:
            conn.logout()
        except Exception:
            pass
