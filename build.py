import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path

def get_platform():
    system = platform.system().lower()
    if system == 'darwin':
        return 'macos'
    elif system == 'windows':
        return 'windows'
    else:
        raise Exception(f'不支持的操作系统: {system}')

def build_app():
    # 获取当前平台
    current_platform = get_platform()
    print(f'当前平台: {current_platform}')
    
    # 确保PyInstaller已安装
    try:
        import PyInstaller
    except ImportError:
        print('正在安装PyInstaller...')
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'], check=True)
    
    # 项目根目录
    root_dir = Path(__file__).parent
    
    # 清理之前的构建文件
    build_dir = root_dir / 'build'
    dist_dir = root_dir / 'dist'
    if build_dir.exists():
        shutil.rmtree(build_dir)
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    
    # 基本的PyInstaller命令
    pyinstaller_args = [
        'pyinstaller',
        '--clean',
        '--name=NetFucker',
        '--noconsole',
        '--onefile',
        'netfucker.py'
    ]
    
    # 根据平台添加特定选项
    if current_platform == 'macos':
        pyinstaller_args.extend([
            '--windowed',
            '--icon=icon.icns',  # 如果有图标的话
            '--target-arch=universal2',  # 支持Intel和Apple Silicon
        ])
    elif current_platform == 'windows':
        pyinstaller_args.extend([
            '--windowed',
            '--icon=icon.ico',  # 如果有图标的话
        ])
    
    # 执行构建
    print('开始构建...')
    subprocess.run(pyinstaller_args, check=True)
    
    # 处理构建结果
    if current_platform == 'macos':
        # 压缩macOS应用
        app_path = dist_dir / 'NetFucker.app'
        if app_path.exists():
            zip_name = 'NetFucker_Darwin.zip'
            shutil.make_archive(
                str(dist_dir / 'NetFucker_Darwin'),
                'zip',
                dist_dir,
                'NetFucker.app'
            )
            print(f'已创建macOS应用压缩包: {zip_name}')
    elif current_platform == 'windows':
        # 压缩Windows可执行文件
        exe_path = dist_dir / 'NetFucker.exe'
        if exe_path.exists():
            zip_name = 'NetFucker_Windows.zip'
            shutil.make_archive(
                str(dist_dir / 'NetFucker_Windows'),
                'zip',
                dist_dir,
                'NetFucker.exe'
            )
            print(f'已创建Windows可执行文件压缩包: {zip_name}')
    
    print('构建完成!')

if __name__ == '__main__':
    try:
        build_app()
    except Exception as e:
        print(f'构建失败: {str(e)}')
        sys.exit(1)