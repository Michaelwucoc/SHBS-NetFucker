import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path

def select_platform():
    print('请选择编译目标平台:')
    print('1 = Windows')
    print('2 = macOS')
    print('A = 所有平台')
    choice = input('请输入选择 (1/2/A): ').strip().upper()
    
    if choice == '1':
        return ['windows']
    elif choice == '2':
        return ['macos']
    elif choice == 'A':
        return ['windows', 'macos']
    else:
        raise Exception('无效的选择')

def build_app():
    # 获取用户选择的平台
    try:
        platforms = select_platform()
    except Exception as e:
        print(f'错误: {str(e)}')
        return
    
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
    
    # 遍历选择的平台进行构建
    for platform_name in platforms:
        print(f'\n开始构建 {platform_name} 版本...')
        
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
        if platform_name == 'macos':
            pyinstaller_args.extend(['--windowed'])
            # 检查图标文件是否存在
            icon_path = root_dir / 'icon.icns'
            if icon_path.exists():
                pyinstaller_args.extend(['--icon=' + str(icon_path)])
            pyinstaller_args.extend(['--target-arch=universal2'])  # 支持Intel和Apple Silicon
        elif platform_name == 'windows':
            pyinstaller_args.extend(['--windowed'])
            # 检查图标文件是否存在
            icon_path = root_dir / 'icon.ico'
            if icon_path.exists():
                pyinstaller_args.extend(['--icon=' + str(icon_path)])
        
        # 执行构建
        print(f'正在构建 {platform_name} 版本...')
        try:
            subprocess.run(pyinstaller_args, check=True)
            
            # 处理构建结果
            if platform_name == 'macos':
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
            elif platform_name == 'windows':
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
        except subprocess.CalledProcessError as e:
            print(f'构建 {platform_name} 版本失败: {str(e)}')
            continue
    
    print('\n所有平台构建完成!')

if __name__ == '__main__':
    try:
        build_app()
    except Exception as e:
        print(f'构建失败: {str(e)}')
        sys.exit(1)