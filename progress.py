from typing import Dict
class Progress:
  def __init__(self, meter_str: str, valuemin: str, valuemax: str, valuenow: str):
    """Represent an aria-style progress meter for Udemy cards.

    Args:
      meter_str (str): Human readable label (e.g., ``"12%完了"``).
      valuemin (str): Minimum value provided by the DOM attribute.
      valuemax (str): Maximum value provided by the DOM attribute.
      valuenow (str): Current progress value.

    Returns:
      None
    """
    self.meter_str = meter_str
    self.valuemin = valuemin
    self.valuemax = valuemax
    self.valuenow = valuenow
    self.meter = f'{self.valuemin}-{self.valuemax}-{self.valuenow}'

  def to_dict(self) -> Dict[str, str]:
    """Expose the progress state as a serializable dict.

    Returns:
      Dict[str, str]: Keys ``meter_str``, ``valuemin``, ``valuemax``,
      ``valuenow``, and ``meter``.
    """
    return {
      'meter_str': self.meter_str,
      'valuemin': self.valuemin,
      'valuemax': self.valuemax,
      'valuenow': self.valuenow,
      'meter': self.meter
    }