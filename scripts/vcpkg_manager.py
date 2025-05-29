#!/usr/bin/env python3
import argparse
import os
import platform
import subprocess
import sys
from pathlib import Path

class VcpkgManager:
    def __init__(self):
        self.system = platform.system().lower()
        self.default_triplets = {
            'linux': 'x64-linux-dynamic',
            'windows': 'x64-windows-v142'
        }
        self.default_archive_names = {
            'linux': 'astra17_515',
            'windows': 'v142_x64'
        }
        self.default_nuget_url = "http://localhost:5555/v3/index.json"
        
    def get_default_triplet(self):
        return self.default_triplets.get(self.system, 'x64-linux-dynamic')
    
    def get_default_archive_name(self):
        return self.default_archive_names.get(self.system, 'default_export')
    
    def setup_environment(self, triplet, cache_type, nuget_url=None):
        """Настройка переменных окружения"""
        env = os.environ.copy()
        
        if self.system == 'windows':
            env['VCPKG_DEFAULT_TRIPLET'] = triplet
            env['VCPKG_KEEP_ENV_VARS'] = 'PATH'
            
            if cache_type == 'local':
                env['VCPKG_BINARY_SOURCES'] = f"clear;files,{os.getcwd()}\\cache,readwrite"
            else:  # remote
                env['VCPKG_BINARY_SOURCES'] = f"clear;nuget,{nuget_url},readwrite;nugettimeout,600"
        else:  # Linux/macOS
            env['VCPKG_DEFAULT_TRIPLET'] = triplet
            
            if cache_type == 'local':
                env['VCPKG_BINARY_SOURCES'] = f"clear;files,{os.getcwd()}/cache,readwrite"
            else:  # remote
                env['VCPKG_BINARY_SOURCES'] = f"clear;nuget,{nuget_url},readwrite;nugettimeout,600"
        
        return env
    
    def run_command(self, command, env):
        """Выполнение команды с обработкой ошибок"""
        print(f"Executing: {' '.join(command) if isinstance(command, list) else command}")
        
        try:
            if self.system == 'windows':
                result = subprocess.run(command, env=env, shell=True, check=True, 
                                      capture_output=False, text=True)
            else:
                result = subprocess.run(command, env=env, shell=False, check=True, 
                                      capture_output=False, text=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error executing command: {e}")
            return False
    
    def install_dependencies(self, env):
        """Установка зависимостей"""
        print("Installing all dependencies...")
        command = ['vcpkg', 'install', '--clean-after-build']
        return self.run_command(command, env)
    
    def export_dependencies(self, archive_name, env):
        """Экспорт зависимостей"""
        print(f"Exporting all installed dependencies to {os.getcwd()}/env/{archive_name}")
        
        if self.system == 'windows':
            output_dir = f"{os.getcwd()}/env"
        else:
            output_dir = f"{os.getcwd()}/env"
        
        command = [
            'vcpkg', 'export', 
            '--x-all-installed', 
            '--7zip', 
            f'--output-dir={output_dir}',
            f'--output={archive_name}'
        ]
        return self.run_command(command, env)
    
    def cleanup_installed(self):
        """Очистка установленных зависимостей"""
        print("Cleaning installed dependencies...")
        
        if self.system == 'windows':
            vcpkg_installed = Path(os.getcwd()) / 'vcpkg_installed'
            if vcpkg_installed.exists():
                command = f'rmdir /S /Q "{vcpkg_installed}"'
                return self.run_command(command, os.environ.copy())
        else:
            vcpkg_installed = Path(os.getcwd()) / 'vcpkg_installed'
            if vcpkg_installed.exists():
                command = ['sudo', 'rm', '-rf', str(vcpkg_installed)]
                return self.run_command(command, os.environ.copy())
        
        return True
    
    def print_cmake_usage(self, triplet):
        """Вывод информации об использовании с CMake"""
        if self.system == 'windows':
            toolchain_path = f"{os.getcwd()}/env/*_x64/scripts/buildsystems/vcpkg.cmake"
        else:
            toolchain_path = f"{os.getcwd()}/env/*/scripts/buildsystems/vcpkg.cmake"
        
        print("\n" + "="*80)
        print("CMAKE USAGE:")
        print(f"-DCMAKE_TOOLCHAIN_FILE={toolchain_path}")
        print(f"-DVCPKG_TARGET_TRIPLET={triplet}")
        print("="*80)
    
    def run_step(self, step_name, args):
        """Выполнение отдельного шага"""
        triplet = args.triplet or self.get_default_triplet()
        archive_name = args.archive or self.get_default_archive_name()
        nuget_url = args.nuget_url or self.default_nuget_url
        
        print(f"System: {self.system}")
        print(f"Triplet: {triplet}")
        print(f"Archive name: {archive_name}")
        print(f"Cache type: {args.cache}")
        if args.cache == 'remote':
            print(f"NuGet URL: {nuget_url}")
        
        # Настройка окружения
        env = self.setup_environment(triplet, args.cache, nuget_url)
        
        print(f"\n--- Executing step: {step_name} ---")
        
        if step_name == 'install':
            success = self.install_dependencies(env)
        elif step_name == 'export':
            success = self.export_dependencies(archive_name, env)
        elif step_name == 'cleanup':
            success = self.cleanup_installed()
        else:
            print(f"Unknown step: {step_name}")
            return False
        
        if success:
            print(f"Step '{step_name}' completed successfully!")
            
            # Показать CMake usage только после install или export
            if step_name in ['install', 'export']:
                self.print_cmake_usage(triplet)
        else:
            print(f"Step '{step_name}' failed!")
        
        return success
    
    def run(self, args):
        """Основная функция выполнения"""
        triplet = args.triplet or self.get_default_triplet()
        archive_name = args.archive or self.get_default_archive_name()
        nuget_url = args.nuget_url or self.default_nuget_url
        
        print(f"System: {self.system}")
        print(f"Triplet: {triplet}")
        print(f"Archive name: {archive_name}")
        print(f"Cache type: {args.cache}")
        if args.cache == 'remote':
            print(f"NuGet URL: {nuget_url}")
        
        # Настройка окружения
        env = self.setup_environment(triplet, args.cache, nuget_url)
        
        # Определение шагов для выполнения
        all_steps = [
            ("install", "Installing dependencies", lambda: self.install_dependencies(env)),
            ("export", "Exporting dependencies", lambda: self.export_dependencies(archive_name, env)),
            ("cleanup", "Cleaning up", lambda: self.cleanup_installed())
        ]
        
        # Фильтрация шагов в зависимости от аргументов
        if hasattr(args, 'steps') and args.steps:
            # Выполнить только указанные шаги
            steps_to_run = []
            for step_id, step_name, step_func in all_steps:
                if step_id in args.steps:
                    steps_to_run.append((step_id, step_name, step_func))
            
            if not steps_to_run:
                print("No valid steps specified!")
                return False
        else:
            # Выполнить все шаги (обратная совместимость)
            steps_to_run = [(step_id, step_name, step_func) for step_id, step_name, step_func in all_steps]
        
        # Выполнение шагов
        for step_id, step_name, step_func in steps_to_run:
            print(f"\n--- {step_name} ---")
            if not step_func():
                print(f"Failed at step: {step_name}")
                return False
        
        # Вывод информации об использовании
        self.print_cmake_usage(triplet)
        
        print("\nAll specified steps completed successfully!")
        return True

def main():
    manager = VcpkgManager()
    
    parser = argparse.ArgumentParser(
        description='VCPKG Manager - Install, export and manage vcpkg dependencies',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  # Use default settings (all steps)
  python3 vcpkg_manager.py
  
  # Only install dependencies
  python3 vcpkg_manager.py --steps install
  
  # Only export dependencies
  python3 vcpkg_manager.py --steps export
  
  # Install and export (skip cleanup)
  python3 vcpkg_manager.py --steps install export
  
  # Use remote cache with custom archive name
  python3 vcpkg_manager.py --cache remote --archive my_deps_v1
  
  # Use custom triplet and only install
  python3 vcpkg_manager.py --triplet x64-linux-static --steps install
  
  # Use custom NuGet server and only install
  python3 vcpkg_manager.py --cache remote --nuget-url http://my-nuget-server.com/v3/index.json --steps install

Available steps:
  install  - Install dependencies using vcpkg
  export   - Export installed dependencies to archive
  cleanup  - Clean up vcpkg_installed directory

Default triplets by OS:
  Linux: {manager.default_triplets['linux']}
  Windows: {manager.default_triplets['windows']}
        """
    )
    
    parser.add_argument(
        '--cache', 
        choices=['local', 'remote'], 
        default='remote',
        help='Cache type: local (files) or remote (NuGet) (default: remote)'
    )
    
    parser.add_argument(
        '--triplet', 
        help=f'VCPKG triplet (default: {manager.get_default_triplet()} for current OS)'
    )
    
    parser.add_argument(
        '--archive', 
        help=f'Archive name for export (default: {manager.get_default_archive_name()} for current OS)'
    )
    
    parser.add_argument(
        '--nuget-url', 
        default=manager.default_nuget_url,
        help=f'NuGet server URL for remote cache (default: {manager.default_nuget_url})'
    )
    
    parser.add_argument(
        '--steps',
        nargs='+',
        choices=['install', 'export', 'cleanup'],
        help='Specify which steps to execute (default: all steps). Can specify multiple steps.'
    )
    
    parser.add_argument(
        '--dry-run', 
        action='store_true',
        help='Show what would be executed without running commands'
    )
    
    args = parser.parse_args()
    
    if args.dry_run:
        print("DRY RUN MODE - Commands that would be executed:")
        print(f"Triplet: {args.triplet or manager.get_default_triplet()}")
        print(f"Archive: {args.archive or manager.get_default_archive_name()}")
        print(f"Cache: {args.cache}")
        if args.cache == 'remote':
            print(f"NuGet URL: {args.nuget_url}")
        
        steps_to_show = args.steps if args.steps else ['install', 'export', 'cleanup']
        print(f"Steps to execute: {', '.join(steps_to_show)}")
        
        # Показать команды для каждого шага
        for step in steps_to_show:
            print(f"\nStep '{step}':")
            if step == 'install':
                print("  vcpkg install --clean-after-build")
            elif step == 'export':
                archive = args.archive or manager.get_default_archive_name()
                print(f"  vcpkg export --x-all-installed --7zip --output-dir={os.getcwd()}/env --output={archive}")
            elif step == 'cleanup':
                if manager.system == 'windows':
                    print(f"  rmdir /S /Q \"{os.getcwd()}\\vcpkg_installed\"")
                else:
                    print(f"  sudo rm -rf {os.getcwd()}/vcpkg_installed")
        return
    
    try:
        success = manager.run(args)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
