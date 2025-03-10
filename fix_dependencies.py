#!/usr/bin/env python3
"""
修复项目依赖问题的脚本
"""

import subprocess
import sys
import os
import platform

def run_command(command):
    """运行命令并返回结果"""
    print(f"执行: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"警告: 命令执行返回非零状态码 {result.returncode}")
        print(f"错误输出: {result.stderr}")
    return result.stdout.strip()

def fix_sqlalchemy_issue():
    """修复 SQLAlchemy 相关问题"""
    print("修复 SQLAlchemy 相关问题...")

    # 卸载可能有冲突的包
    run_command("pip uninstall -y sqlalchemy flask-sqlalchemy alembic flask-migrate")

    # 按照特定顺序安装兼容的版本
    run_command("pip install SQLAlchemy==1.4.46")
    run_command("pip install Flask-SQLAlchemy==2.5.1")
    run_command("pip install alembic==1.7.7")
    run_command("pip install Flask-Migrate==3.1.0")

    print("SQLAlchemy 相关依赖已修复。")

def fix_werkzeug_issue():
    """修复 Werkzeug 相关问题"""
    print("修复 Werkzeug 相关问题...")

    # 卸载可能有冲突的包
    run_command("pip uninstall -y werkzeug flask")

    # 按照特定顺序安装兼容的版本
    run_command("pip install Werkzeug==2.0.3")
    run_command("pip install Flask==2.0.1")

    print("Werkzeug 相关依赖已修复。")

def check_environment():
    """检查环境并打印信息"""
    print("\n环境信息:")
    print(f"Python 版本: {platform.python_version()}")
    print(f"操作系统: {platform.platform()}")

    # 检查是否在虚拟环境中
    in_venv = sys.prefix != sys.base_prefix
    print(f"在虚拟环境中: {'是' if in_venv else '否'}")

    if not in_venv:
        print("警告: 你不在虚拟环境中。建议在虚拟环境中运行此脚本。")

    # 列出已安装的关键包
    print("\n已安装的关键包:")
    packages = ["flask", "werkzeug", "sqlalchemy", "flask-sqlalchemy", "flask-migrate", "alembic"]
    for package in packages:
        try:
            version = run_command(f"pip show {package} | grep Version")
            if version:
                print(f"{package}: {version.split(':')[1].strip()}")
            else:
                print(f"{package}: 未安装")
        except Exception as e:
            print(f"{package}: 错误 - {str(e)}")

def main():
    """主函数"""
    print("开始修复项目依赖问题...")

    # 检查环境
    check_environment()

    # 询问用户要修复哪个问题
    print("\n请选择要修复的问题:")
    print("1. SQLAlchemy 相关问题 (AttributeError: module 'sqlalchemy' has no attribute '__all__')")
    print("2. Werkzeug 相关问题 (ImportError: cannot import name 'url_quote' from 'werkzeug.urls')")
    print("3. 全部修复")
    print("4. 只检查环境，不修复")
    print("0. 退出")

    choice = input("请输入选项编号: ")

    if choice == "1":
        fix_sqlalchemy_issue()
    elif choice == "2":
        fix_werkzeug_issue()
    elif choice == "3":
        fix_sqlalchemy_issue()
        fix_werkzeug_issue()
    elif choice == "4":
        print("已完成环境检查，不执行修复。")
    elif choice == "0":
        print("退出脚本。")
        return
    else:
        print("无效选项，退出脚本。")
        return

    # 重新安装所有依赖
    print("\n重新安装所有项目依赖...")
    run_command("pip install -r requirements.txt")

    # 最终检查
    print("\n修复完成。最终环境信息:")
    check_environment()

    print("\n如果你仍然遇到问题，请考虑重新创建虚拟环境并从头开始。")

if __name__ == "__main__":
    main()