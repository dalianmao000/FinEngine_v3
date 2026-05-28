import yaml
from pathlib import Path


class ScenarioRouter:
    """场景路由器，加载YAML配置"""

    def __init__(self, scenarios_dir: str = "app/scenarios"):
        self.scenarios_dir = Path(scenarios_dir)
        self._cache: dict[str, dict] = {}

    def load_scenario(self, scenario_name: str) -> dict:
        if scenario_name in self._cache:
            return self._cache[scenario_name]

        config_path = self.scenarios_dir / f"{scenario_name}.yaml"
        if not config_path.exists():
            raise FileNotFoundError(f"Scenario config not found: {config_path}")

        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        self._cache[scenario_name] = config
        return config

    def list_scenarios(self) -> list[str]:
        return [p.stem for p in self.scenarios_dir.glob("*.yaml")]