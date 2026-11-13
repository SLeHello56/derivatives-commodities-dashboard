import pandas as pd
from derivatives_dashboard.historical import fetch_spot_reference

class FakeResponse:
    text="observation_date,DCOILWTICO\n2026-01-01,70.2\n2026-01-02,.\n"
    def raise_for_status(self): pass

def test_fred_spot_parser(monkeypatch):
    monkeypatch.setattr("derivatives_dashboard.historical.requests.get",lambda *a,**kw:FakeResponse())
    result=fetch_spot_reference()
    assert len(result)==1
    assert result.spot_reference.iloc[0]==70.2
