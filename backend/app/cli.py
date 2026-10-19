"""Yönetim komutları.

    python -m app.cli create-admin --email yonetici@kurum.org --name "Ad Soyad"

Şifre ekrandan sorulur (veya ADMIN_PASSWORD ortam değişkeninden okunur); komut geçmişine düşmez.
Yönetici hesabı kayıt formundan açılamaz; tek yol budur.
"""

import argparse
import getpass
import os
import sys

from sqlalchemy import select

from app.core.db import SessionLocal
from app.core.security import hash_password
from app.models import Role, User


def create_admin(email: str, name: str, password: str) -> str:
    email = email.strip().lower()
    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.email == email))
        if user is not None and user.role != Role.ADMIN:
            raise SystemExit(f"{email} zaten {user.role} rolünde bir hesap; başka bir e-posta kullanın.")
        if user is None:
            user = User(email=email, full_name=name, role=Role.ADMIN, password_hash=hash_password(password))
            db.add(user)
            result = "oluşturuldu"
        else:
            user.password_hash = hash_password(password)
            result = "şifresi güncellendi"
        db.commit()
    return result


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="python -m app.cli")
    commands = parser.add_subparsers(dest="command", required=True)
    admin = commands.add_parser("create-admin", help="Yönetici hesabı oluşturur veya şifresini yeniler")
    admin.add_argument("--email", required=True)
    admin.add_argument("--name", default="Yönetici")
    args = parser.parse_args(argv)

    password = os.environ.get("ADMIN_PASSWORD") or getpass.getpass("Şifre (en az 12 karakter): ")
    if len(password) < 12:
        sys.exit("Yönetici şifresi en az 12 karakter olmalı.")
    print(f"{args.email}: {create_admin(args.email, args.name, password)}")


if __name__ == "__main__":
    main()
