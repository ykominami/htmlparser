from pathlib import Path
from typing import List, Optional
import yaml

class Env:
    def __init__(self, config_path: Path = None):
        self.base_path = None
        self.pattern = None
        self.config = None
        self.assoc = {}
        if config_path is not None:
            with open(config_path, 'r', encoding='utf-8') as f:
                self.assoc = yaml.load(f, Loader=yaml.FullLoader)
                base_path_array = self.assoc['base_path']
                self.base_path = self.make_path(base_path_array)

    def make_path(self, path_array: list[str]) -> Path:
          # print(f"path_array={path_array}")
          if path_array is not None:
            top_dir = path_array.pop(0)
            top_path = Path(top_dir)
            base_path = top_path / Path( *path_array)
          else:
            base_path = Path(".").resolve()

          return base_path

    def mode(self):
      mode = self.config['mode']
      if mode is None:
        mode = "H3"
      return mode

    def set_base_path(self, base_path: Path):
        self.base_path = base_path

    def set_pattern(self, pattern: str):
        """
        指定されたアソシエーションキーに対応する項目を記録し、かつ帰す
        
        Args:
            assoc_key: self.assoc内のキー（例: 'Udemy-2-file', 'Udemy-2-dir'）
        
        Returns:
            Pathオブジェクトのリスト
        """
        self.pattern = pattern
        if pattern not in self.assoc:
            print(f"pattern={pattern} not found")
            self.config = {'mode': 'H3'}
            return None
        self.config = self.assoc[pattern]
        return self.config

    def get_files(self) -> List[Path]:
        """
        記録された項目のファイルのリストを返す
        
        Args:
            assoc_key: self.assoc内のキー（例: 'Udemy-2-file', 'Udemy-2-dir'）
        
        Returns:
            Pathオブジェクトのリスト
        """
        print(f"2 self.config={self.config}")
        if self.config is None:
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
        """
        assoc辞書をYAML形式で出力する
        
        Args:
            output_path: 出力先のファイルパス。Noneの場合は文字列として返す
        
        Returns:
            YAML形式の文字列
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
