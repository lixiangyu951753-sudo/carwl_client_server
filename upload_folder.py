# 上传文件夹到OSS

import alibabacloud_oss_v2 as oss
import os

BUCKET_NAME = 'nexus-crawl-data-dev'
REGION = 'cn-shenzhen'
OSS_FOLDER = 'temp/'  # OSS中的文件夹前缀

def upload_folder(local_folder, oss_prefix=''):
    """上传整个文件夹到OSS"""
    
    # 初始化OSS客户端
    credentials_provider = oss.credentials.EnvironmentVariableCredentialsProvider()
    cfg = oss.config.load_default()
    cfg.credentials_provider = credentials_provider
    cfg.region = REGION
    client = oss.Client(cfg)

    # 获取文件夹中的所有文件
    files = []
    for root, dirs, filenames in os.walk(local_folder):
        for filename in filenames:
            local_path = os.path.join(root, filename)
            files.append(local_path)
    
    print(f"找到 {len(files)} 个文件")
    
    # 上传每个文件
    success_count = 0
    fail_count = 0
    
    for local_path in files:
        # 计算OSS中的key（保留相对路径结构）
        rel_path = os.path.relpath(local_path, local_folder)
        oss_key = oss_prefix + rel_path.replace('\\', '/')
        
        try:
            result = client.put_object_from_file(
                oss.PutObjectRequest(
                    bucket=BUCKET_NAME,
                    key=oss_key
                ),
                local_path
            )
            
            if result.status_code == 200:
                print(f"✓ 上传成功: {rel_path}")
                success_count += 1
            else:
                print(f"✗ 上传失败: {rel_path}")
                fail_count += 1
                
        except Exception as e:
            print(f"✗ 错误: {rel_path} - {e}")
            fail_count += 1
    
    print(f"\n上传完成！成功: {success_count}, 失败: {fail_count}")

def main():
    """主函数"""
    # 要上传的本地文件夹
    local_folder = 'D:\\works\\crawl\\1688\\'
    
    # 检查文件夹是否存在
    if not os.path.exists(local_folder):
        print(f"错误: 文件夹不存在: {local_folder}")
        return
    
    if not os.path.isdir(local_folder):
        print(f"错误: 路径不是文件夹: {local_folder}")
        return
    
    # 直接使用默认的 OSS_FOLDER
    oss_prefix = OSS_FOLDER
    
    print(f"\n开始上传...")
    print(f"本地文件夹: {local_folder}")
    print(f"OSS前缀: {oss_prefix}")
    print("-" * 50)
    
    upload_folder(local_folder, oss_prefix)

if __name__ == "__main__":
    main()
