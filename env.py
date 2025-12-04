from pathlib import Path
from typing import List, Optional
import yaml

class Env:
    def __init__(self, config_path: Path = None):
        """Load configuration and initialize base path/mode settings.

        Args:
            config_path (Path | None): YAML containing ``base_path`` and pattern
                associations. When ``None`` the environment starts empty.

        Returns:
            None
        """
        self.base_path = None
        self.pattern = None
        self.config = {}
        self.assoc = {}
        if config_path is not None:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.assoc = yaml.load(f, Loader=yaml.FullLoader)
                # self.config.update(self.assoc)
                base_path_array = self.assoc['base_path']
                self.base_path = self.make_path(base_path_array)
                # print(f'self.assoc={self.assoc}')
                # print(f'self.config={self.config}')
                # exit(0)

    def make_path(self, path_array: list[str]) -> Path | None:
        """Convert a sequence of path components into a concrete path.

        Args:
            path_array (list[str]): Ordered segments such as
                ``['C:/data', 'courses']``.

        Returns:
            Path | None: Composed path or ``None`` when no components exist.
        """
        base_path = None
        # print(f"path_array={path_array}")
        if path_array is not None:
            top_dir = path_array.pop(0)
            top_path = Path(top_dir)
            base_path = top_path / Path( *path_array)

        return base_path

    def mode(self):
        """Return the scraper mode stored in the active pattern.

        Returns:
            str: Mode string, defaulting to ``"H3"`` when unspecified.
        """
        mode = self.config['mode']
        if mode is None:
            mode = "H3"
        return mode

    def set_base_path(self, base_path: Path):
        """Persist an externally provided root directory.

        Args:
            base_path (Path): Directory serving as the root for pattern paths.

        Returns:
            None
        """
        self.base_path = base_path

    def set_pattern(self, pattern: str):
        """Load the configuration block associated with ``pattern``.

        Args:
            pattern (str): Key in ``assoc`` (e.g., ``'Udemy-2-file'``).

        Returns:
            dict | None: Selected configuration or ``None`` when unknown.
        """
        self.pattern = pattern
        if pattern not in self.assoc:
            print(f"pattern={pattern} not found")
            self.config['mode'] = 'H3'
            return None
        self.config = self.assoc[ pattern ]
        return self.config

    def get_files(self) -> List[Path]:
        """Resolve the files or directory contents defined by the pattern.

        Returns:
            List[Path]: Concrete file paths ready for scraping.
        """
        print(f"2 self.config={self.config}")
        if len(self.config) == 0:
          return []
        else:
          print(f"Env get_files self.config={self.config}")
          print(f"Env get_files self.config['dir']={self.config['dir']}")
          dir_path = self.base_path / Path(*self.config['dir'])
          
          if self.config['kind'] == 'file':
            # 指定されたファイルのみを返す
            files = self.config.get('files', [])
            return [dir_path / file for file in files]
          else:
            # 指定ディレクトリの直下に存在するファイルの一覧を返す
            if not dir_path.exists() or not dir_path.is_dir():
                return []
            files = [f for f in dir_path.iterdir() if f.is_file()]
            return sorted(files)
    
    def output_yaml(self, output_path: Optional[Path] = None) -> str:
        """Dump the association map to YAML and optionally write it to disk.

        Args:
            output_path (Path | None): Destination path. ``None`` returns the
                YAML string without writing.

        Returns:
            str: YAML serialization of ``assoc``.
        """
        yaml_str = yaml.dump(self.assoc, default_flow_style=False, 
                            allow_unicode=True, sort_keys=False)
        
        if output_path is not None:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(yaml_str)
        
        return yaml_str


if __name__ == "__main__":
    # 使用例
    # または相対パスを使用する場合：
    # base_path = Path(".")
    path = Path("config.yaml")
    env = Env(path)
    # env.set_base_path(base_path)
    
    patterns = ['Amazon-1-file', 'Amazon-1-dir', 'Amazon-2-file', 'Amazon-2-dir', 'Amazon-10-file', 'Amazon-10-dir', 'Amazon-11-file', 'Amazon-11-dir', 'Amazon-111-file', 'Amazon-111-dir', 'Udemy-1-file', 'Udemy-1-dir', 'Udemy-2-file', 'Udemy-2-dir']
    for pattern in patterns:
        print(f"=== '{pattern}' の使用例 ===")
        env.set_pattern(pattern)
        files = env.get_files()
        print(f"見つかったファイル数: {len(files)}")
        for file in files:
            print(f"  - {file}")

    '''
    # 'Udemy-2-file'の使用例
    print("=== 'Udemy-2-file' の使用例 ===")
    env.set_pattern('Udemy-2-file')
    files = env.get_files()
    print(f"見つかったファイル数: {len(files)}")
    for file in files:
        print(f"  - {file}")
        if file.exists():
            print(f"    (存在します)")
        else:
            print(f"    (存在しません)")
    
    print()
    
    # 'Udemy-2-dir'の使用例
    print("=== 'Udemy-2-dir' の使用例 ===")
    env.set_pattern('Udemy-2-dir')
    dir_files = env.get_files()
    print(f"見つかったファイル数: {len(dir_files)}")
    for file in dir_files:
        print(f"  - {file}")
    
    print()
    
    # 存在しないキーの場合
    print("=== 存在しないキーの場合 ===")
    env.set_pattern('存在しないキー')
    invalid_files = env.get_files()
    print(f"見つかったファイル数: {len(invalid_files)}")

    # env = Env(base_path)

    # 文字列として取得
    yaml_str = env.output_yaml()
    # print(yaml_str)

    # ファイルに出力
    env.output_yaml(Path("output.yaml"))
    '''
