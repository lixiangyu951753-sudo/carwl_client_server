"""
批量复制 .env.development 文件脚本
从源目录复制到目标目录，保持目录结构
"""
import os
import shutil
from pathlib import Path

# 源目录配置
SOURCE_BASE = r'D:\works\ecomops\repo'

# 目标目录配置
TARGET_BASE = r'D:\works\ecomops\repo-add-crawl-oss'

# 需要复制文件的子目录列表
SUB_DIRS = [
    'apps/admin',
    'apps/api',
    'apps/web',
    'services/aigc-service',
    'services/file-service',
    'services/product-center',
    'services/user-center'
]

# 要复制的文件名
FILE_NAME = '.env.development'


def copy_env_file():
    """复制 .env.development 文件"""
    print("=" * 60)
    print("批量复制 .env.development 文件")
    print("=" * 60)
    
    success_count = 0
    skip_count = 0
    error_count = 0
    
    for sub_dir in SUB_DIRS:
        source_path = os.path.join(SOURCE_BASE, sub_dir, FILE_NAME)
        target_path = os.path.join(TARGET_BASE, sub_dir, FILE_NAME)
        
        print(f"\n处理: {sub_dir}")
        
        # 检查源文件是否存在
        if not os.path.exists(source_path):
            print(f"  ⚠ 源文件不存在，跳过: {source_path}")
            skip_count += 1
            continue
        
        # 确保目标目录存在
        target_dir = os.path.dirname(target_path)
        os.makedirs(target_dir, exist_ok=True)
        
        # 复制文件
        try:
            shutil.copy2(source_path, target_path)
            print(f"  ✓ 已复制: {source_path}")
            print(f"    到: {target_path}")
            success_count += 1
        except Exception as e:
            print(f"  ✗ 复制失败: {e}")
            error_count += 1
    
    # 输出统计
    print("\n" + "=" * 60)
    print("复制完成！")
    print(f"  成功: {success_count}")
    print(f"  跳过: {skip_count}")
    print(f"  失败: {error_count}")
    print("=" * 60)


if __name__ == '__main__':
    copy_env_file()
