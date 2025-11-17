from pathlib import Path
from typing import Optional
import yaml

class Util:
  def flatten(cls, items):
      """ネストしたリストを平坦化する"""
      flat_list = []
      for item in items:
          if isinstance(item, list):
              flat_list.extend(cls.flatten(item))
          else:
              flat_list.append(item)

      return flat_list

  @classmethod
  def load_yaml(cls, input_path: Path) -> dict:
      """
      YAMLファイルを読み込んでdictを返す
      
      Args:
          input_path: 読み込むYAMLファイルのパス
      
      Returns:
          読み込んだYAMLの内容を表す辞書
      """
      with open(input_path, 'r', encoding='utf-8') as f:
          data = yaml.load(f, Loader=yaml.FullLoader)
      return data

  @classmethod
  def output_yaml(cls, assoc: dict, output_path: Optional[Path] = None) -> str:
      """
      assoc辞書をYAML形式で出力する
      
      Args:
          assoc: YAML形式で出力する辞書
          output_path: 出力先のファイルパス。Noneの場合は文字列として返す
      
      Returns:
          YAML形式の文字列
      """
      yaml_str = yaml.dump(assoc, default_flow_style=False, 
                          allow_unicode=True, sort_keys=False)
      
      if output_path is not None:
          with open(output_path, 'w', encoding='utf-8') as f:
              f.write(yaml_str)
      
      return yaml_str

if __name__ == "__main__":
  input_path = Path('output_2.yaml')
  input_path_2 = Path('output_3.yaml')
  output_path = Path('output_4.yaml')
  dict = Util.load_yaml(input_path)
  dict_2 = Util.load_yaml(input_path_2)

  for key_2, value_2 in dict_2.items():
    value_2['Time'] = '0時間'
    if key_2 in dict.keys():
      value = dict[key_2]
      if 'Time' in value.keys():
        value_2['Time'] = value['Time']

  Util.output_yaml(dict_2, output_path)