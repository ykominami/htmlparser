import sys
from typing import List, Dict
from pathlib import Path
from util import Util

class Store:
  def __init__(self):
    """Hold merged YAML associations for CLI usage.

    Returns:
      None
    """
    self.assoc = {}


if __name__ == "__main__":
  store = Store()
  print(store.assoc)
  input_file = sys.argv[1] if len(sys.argv) > 1 else None
  output_file = sys.argv[2] if len(sys.argv) > 2 else None
  if input_file:
    input_file_path = Path(input_file)
    assoc = Util.load_yaml(input_file_path)
    store.assoc.update(assoc)
    print(f'store.assoc={store.assoc}')
    if output_file:
      print(f'output_file={output_file}')
      output_file_path = Path(output_file)
      Util.output_yaml(store.assoc, output_file_path)
