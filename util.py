from pathlib import Path
from typing import Optional, Sequence
import csv
from io import StringIO
import yaml

class Util:
  @classmethod
  def flatten(cls, items):
      """Flatten arbitrarily nested iterables into a single list.

      Args:
          items (Iterable): Possibly nested lists/tuples of values.

      Returns:
          list: Flattened sequence preserving order.
      """
      flat_list = []
      for item in items:
          if isinstance(item, list):
              flat_list.extend(cls.flatten(item))
          else:
              flat_list.append(item)

      return flat_list

  @classmethod
  def load_yaml(cls, input_path: Path) -> dict:
      """Load a YAML file and return it as a dictionary.

      Args:
          input_path (Path): Path to the YAML file.

      Returns:
          dict: Parsed YAML content.
      """
      data = None
      with open(input_path, 'r', encoding='utf-8') as f:
          data = yaml.load(f, Loader=yaml.FullLoader)
      return data

  @classmethod
  def output_yaml(cls, assoc: dict, output_path: Optional[Path] = None) -> str:
      """Serialize a dictionary to YAML and optionally write it to disk.

      Args:
          assoc (dict): Data to dump.
          output_path (Path | None): Destination path. When ``None`` the YAML
              string is merely returned.

      Returns:
          str: YAML representation of ``assoc``.
      """
      yaml_str = yaml.dump(assoc, default_flow_style=False, 
                          allow_unicode=True, sort_keys=False)
      
      if output_path is not None:
          with open(output_path, 'w', encoding='utf-8') as f:
              f.write(yaml_str)
      
      return yaml_str

  @classmethod
  def load_tsv(cls, input_path: Path, fieldnames: Optional[Sequence[str]] = None) -> list[dict]:
      """Read a TSV file and convert rows into dictionaries.

      Args:
          input_path (Path): TSV file path.
          fieldnames (Sequence[str] | None): Explicit headers. When ``None`` the
              first row becomes the header.

      Returns:
          list[dict]: Each row keyed by the header columns.

      Raises:
          ValueError: If no headers can be determined.
      """
      records = []
      with open(input_path, 'r', encoding='utf-8', newline='') as f:
          reader = csv.reader(f, delimiter='\t')
          headers = list(fieldnames) if fieldnames is not None else None

          for row in reader:
              if headers is None:
                  headers = row
                  continue
              record = {key: value for key, value in zip(headers, row)}
              records.append(record)

      if headers is None:
          raise ValueError("ヘッダー行が存在しません。fieldnamesを指定してください。")

      return records

  @classmethod
  def output_tsv(
      cls,
      records: Sequence[dict],
      output_path: Optional[Path] = None,
      fieldnames: Optional[Sequence[str]] = None
  ) -> str:
      """Write record dictionaries to TSV format.

      Args:
          records (Sequence[dict]): Rows to emit.
          output_path (Path | None): Optional destination file.
          fieldnames (Sequence[str] | None): Header order override; defaults to
              keys of the first record.

      Returns:
          str: TSV string containing the headers and rows.

      Raises:
          ValueError: If neither records nor ``fieldnames`` are provided.
      """
      if not records and fieldnames is None:
          raise ValueError("fieldnamesを指定するか、recordsに1件以上のデータを含めてください。")

      headers = list(fieldnames) if fieldnames is not None else list(records[0].keys())

      buffer = StringIO()
      writer = csv.writer(buffer, delimiter='\t', lineterminator='\n')
      writer.writerow(headers)
      for record in records:
          row = [record.get(header, "") for header in headers]
          writer.writerow(row)

      tsv_str = buffer.getvalue()

      if output_path is not None:
          with open(output_path, 'w', encoding='utf-8', newline='') as f:
              f.write(tsv_str)

      return tsv_str

  def test_yaml(self):
    """Developer helper for merging Udemy YAML progress data.

    Returns:
      None
    """
    input_path = Path('output_2.yaml')
    input_path_2 = Path('output_udemy_3.yaml')
    output_path = Path('output_4.yaml')
    dict = Util.load_yaml(input_path)
    dict_2 = Util.load_yaml(input_path_2)

    for key_2, value_2 in dict_2.items():
        value_2['Time'] = '0時間'
        if key_2 in dict.keys():
            value = dict[key_2]
            if 'Time' in value.keys():
                value_2['Time'] = value['Time']
        else:
            value_2['Time'] = '0時間'

    Util.output_yaml(dict_2, output_path)
  def test_tsv(self):
    """Developer helper for merging Udemy TSV progress data.

    Returns:
      None
    """
    input_path = Path('output_2.tsv')
    input_path_2 = Path('output_udemy_3.tsv')
    output_path = Path('output_4.tsv')
    dict = Util.load_tsv(input_path)
    dict_2 = Util.load_tsv(input_path_2)
    for record_2 in dict_2:
        record_2['Time'] = '0時間'
        if record_2['Course_ID'] in dict.keys():
            record = dict[record_2['Course_ID']]
            if 'Time' in record.keys():
                record_2['Time'] = record['Time']
        else:
            record_2['Time'] = '0時間'
    Util.output_tsv(dict_2, output_path)

if __name__ == "__main__":
    test_util = Util()
    # test_util.test_yaml()
    test_util.test_tsv()
    