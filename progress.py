class Progress:
  def __init__(self, meter_str: str, valuemin: str, valuemax: str, valuenow: str):
    self.meter_str = meter_str
    self.valuemin = valuemin
    self.valuemax = valuemax
    self.valuenow = valuenow
    self.meter = f'{self.valuemin}-{self.valuemax}-{self.valuenow}'

  def to_dict(self) -> dict:
    """YAML形式に変換可能な辞書を返す"""
    return {
      'meter_str': self.meter_str,
      'valuemin': self.valuemin,
      'valuemax': self.valuemax,
      'valuenow': self.valuenow,
      'meter': self.meter
    }