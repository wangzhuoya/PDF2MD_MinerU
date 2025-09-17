#!/usr/bin/env python3
"""
完整的MinerU PDF转Markdown转换脚本
包含上传、等待处理、下载和解压功能
"""

import requests
import time
import os
import zipfile
from pathlib import Path
import json
from dotenv import load_dotenv

class MinerUConverter:
    def __init__(self, token):
        if not token:
            raise ValueError("MinerU API token is required.")
        self.token = token
        self.base_url = "https://mineru.net"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
    
    def upload_and_convert_pdf(self, pdf_path, output_dir="data/01_data/arxiv_md", max_wait_time=600):
        """
        完整的PDF转换流程：上传 -> 等待处理 -> 下载 -> 解压
        
        Args:
            pdf_path (str): PDF文件路径
            output_dir (str): 输出目录
            max_wait_time (int): 最大等待时间（秒）
        
        Returns:
            bool: 转换是否成功
        """
        pdf_file = Path(pdf_path)
        if not pdf_file.exists():
            print(f"❌ PDF文件不存在: {pdf_path}")
            return False
        
        print(f"🚀 开始转换PDF: {pdf_file.name}")
        
        # 步骤1: 申请上传URL
        batch_id = self._request_upload_urls([pdf_file.name])
        if not batch_id:
            return False
        
        # 步骤2: 上传PDF文件
        if not self._upload_pdf_file(batch_id, pdf_path):
            return False
        
        # 步骤3: 等待处理完成
        download_url = self._wait_for_completion(batch_id, max_wait_time)
        if not download_url:
            return False
        
        # 步骤4: 下载并解压结果
        return self._download_and_extract(download_url, pdf_file.stem, output_dir)
    
    def _request_upload_urls(self, file_names):
        """申请上传URL"""
        url = f"{self.base_url}/api/v4/file-urls/batch"
        
        data = {
            "enable_formula": True,
            "language": "auto", 
            "enable_table": True,
            "files": [{"name": name, "is_ocr": True} for name in file_names],
            "model_version": "vlm"
        }
        
        try:
            print("📤 申请上传URL...")
            response = requests.post(url, headers=self.headers, json=data)
            
            if response.status_code == 200:
                result = response.json()
                if result["code"] == 0:
                    batch_id = result["data"]["batch_id"]
                    urls = result["data"]["file_urls"]
                    print(f"✅ 获取上传URL成功，batch_id: {batch_id}")
                    
                    # 存储上传URL供后续使用
                    self.upload_urls = urls
                    return batch_id
                else:
                    print(f"❌ 申请上传URL失败: {result.get('msg', 'Unknown error')}")
                    return None
            else:
                print(f"❌ 请求失败，状态码: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ 申请上传URL异常: {e}")
            return None
    
    def _upload_pdf_file(self, batch_id, pdf_path):
        """上传PDF文件"""
        try:
            print("📤 上传PDF文件...")
            
            with open(pdf_path, 'rb') as f:
                # 使用第一个上传URL
                upload_url = self.upload_urls[0]
                response = requests.put(upload_url, data=f)
                
                if response.status_code == 200:
                    print("✅ PDF文件上传成功")
                    return True
                else:
                    print(f"❌ PDF文件上传失败，状态码: {response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"❌ 上传PDF文件异常: {e}")
            return False
    
    def _wait_for_completion(self, batch_id, max_wait_time):
        """等待处理完成"""
        url = f"{self.base_url}/api/v4/extract-results/batch/{batch_id}"
        
        print(f"⏳ 等待处理完成（最大等待时间: {max_wait_time}秒）...")
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            try:
                response = requests.get(url, headers=self.headers)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if result["code"] == 0:
                        data = result["data"]
                        extract_results = data["extract_result"]
                        
                        for file_result in extract_results:
                            state = file_result["state"]
                            file_name = file_result["file_name"]
                            
                            print(f"📊 文件 {file_name} 状态: {state}")
                            
                            if state == "done":
                                download_url = file_result["full_zip_url"]
                                print(f"✅ 处理完成！下载URL: {download_url}")
                                return download_url
                            elif state == "failed":
                                error_msg = file_result.get("err_msg", "Unknown error")
                                print(f"❌ 处理失败: {error_msg}")
                                return None
                            elif state in ["processing", "pending", "uploaded"]:
                                # 继续等待
                                pass
                    else:
                        print(f"❌ 查询状态失败: {result.get('msg', 'Unknown error')}")
                        return None
                else:
                    print(f"❌ 查询状态请求失败，状态码: {response.status_code}")
                    return None
                    
            except Exception as e:
                print(f"❌ 查询状态异常: {e}")
                return None
            
            # 等待10秒后再次查询
            print("⏳ 等待10秒后重新查询...")
            time.sleep(10)
        
        print(f"❌ 处理超时（{max_wait_time}秒）")
        return None
    
    def _download_and_extract(self, download_url, file_stem, output_dir):
        """下载并解压ZIP文件"""
        try:
            # 创建ZIP存储目录
            zip_storage_dir = Path("/home/wang2go/Code/CNOOC_RAG/CNOOC_RAG/data/00_raw/arxiv_pdf_mineru")
            zip_storage_dir.mkdir(parents=True, exist_ok=True)
            
            # 创建Markdown输出目录
            md_output_dir = Path("/home/wang2go/Code/CNOOC_RAG/CNOOC_RAG/data/01_data/arxiv_md")
            md_output_dir.mkdir(parents=True, exist_ok=True)
            
            # 下载ZIP文件
            print("📥 下载转换结果...")
            zip_response = requests.get(download_url)
            
            if zip_response.status_code == 200:
                zip_filename = f"{file_stem}_converted.zip"
                zip_path = zip_storage_dir / zip_filename
                
                with open(zip_path, 'wb') as f:
                    f.write(zip_response.content)
                
                print(f"✅ ZIP文件下载成功: {zip_path}")
                
                # 解压ZIP文件到临时目录
                print("📂 解压ZIP文件...")
                temp_extract_dir = zip_storage_dir / f"{file_stem}_temp"
                temp_extract_dir.mkdir(exist_ok=True)
                
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_extract_dir)
                
                print(f"✅ 文件解压成功: {temp_extract_dir}")
                
                # 查找并移动Markdown文件到指定目录
                success = self._organize_extracted_files(temp_extract_dir, md_output_dir, file_stem)
                
                # 删除ZIP文件和临时解压目录
                print("🗑️ 清理临时文件...")
                zip_path.unlink()  # 删除ZIP文件
                
                # 删除临时解压目录
                import shutil
                shutil.rmtree(temp_extract_dir)
                
                print("✅ 临时文件清理完成")
                
                return success
            else:
                print(f"❌ 下载ZIP文件失败，状态码: {zip_response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 下载解压异常: {e}")
            return False
    
    def _organize_extracted_files(self, extract_dir, output_dir, file_stem):
        """整理解压后的文件"""
        try:
            # 查找Markdown文件 - 尝试多种可能的文件名
            md_patterns = ["**/full.md", "**/*.md", "**/content.md", "**/output.md", "**/auto/*.md"]
            md_files = []
            
            for pattern in md_patterns:
                md_files = list(extract_dir.glob(pattern))
                if md_files:
                    print(f"📋 找到Markdown文件，模式: {pattern}")
                    break
            
            if md_files:
                # 选择最大的Markdown文件（通常是主文件）
                main_md = max(md_files, key=lambda x: x.stat().st_size)
                target_md = output_dir / f"{file_stem}.md"
                
                # 如果目标文件已存在，先删除
                if target_md.exists():
                    target_md.unlink()
                
                # 复制文件内容（避免跨设备移动问题）
                with open(main_md, 'r', encoding='utf-8') as src:
                    content = src.read()
                
                with open(target_md, 'w', encoding='utf-8') as dst:
                    dst.write(content)
                
                file_size_kb = target_md.stat().st_size / 1024
                print(f"📝 Markdown文件已保存: {target_md} ({file_size_kb:.1f} KB)")
                
                return True
            else:
                print("⚠️ 未找到Markdown文件")
                # 列出所有文件以便调试
                all_files = list(extract_dir.glob("**/*"))
                print("📁 解压后的所有文件:")
                for file in all_files[:10]:  # 显示前10个文件
                    if file.is_file():
                        size_kb = file.stat().st_size / 1024
                        print(f"   - {file.name} ({size_kb:.1f} KB)")
                
                return False
                
        except Exception as e:
            print(f"❌ 整理文件异常: {e}")
            return False

def main():
    """主函数 - 测试转换功能"""
    load_dotenv()
    TOKEN = os.getenv("MINERU_API_TOKEN")
    
    # 测试的PDF文件路径
    test_pdf = "/home/wang2go/Code/CNOOC_RAG/CNOOC_RAG/data/00_raw/arxiv_pdf/0803.1080.pdf"

    # 保存转换后的markdow文件路径
    output_dir = "/home/wang2go/Code/CNOOC_RAG/CNOOC_RAG/data/01_data/arxiv_md"
    
    # 创建转换器
    converter = MinerUConverter(TOKEN)
    
    # 执行转换
    success = converter.upload_and_convert_pdf(pdf_path=test_pdf, output_dir=output_dir)
    
    if success:
        print("🎉 PDF转换完成！")
    else:
        print("❌ PDF转换失败！")

if __name__ == "__main__":
    main()

