#!/usr/bin/env python3
"""
生成安全的随机密钥，用于设置环境变量
"""

import secrets
import argparse

def generate_key(length=32):
    """生成指定长度的随机十六进制密钥"""
    return secrets.token_hex(length)

def main():
    parser = argparse.ArgumentParser(description='生成安全的随机密钥')
    parser.add_argument('--length', type=int, default=32,
                        help='密钥长度（字节数，默认32）')
    parser.add_argument('--count', type=int, default=2,
                        help='生成密钥的数量（默认2）')

    args = parser.parse_args()

    print("生成的安全密钥：")
    print("-" * 50)

    for i in range(args.count):
        key = generate_key(args.length)
        print(f"密钥 {i+1}: {key}")

    print("-" * 50)
    print("\n环境变量设置示例：")
    print("SECRET_KEY=" + generate_key(args.length))
    print("JWT_SECRET_KEY=" + generate_key(args.length))

if __name__ == "__main__":
    main()