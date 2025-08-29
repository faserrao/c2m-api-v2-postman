# LLM Agent Factory Design Pattern (Python Guide)

This guide helps you build a scalable, pluggable architecture to support multiple LLM agent implementations (e.g., OpenAI, Claude, Akash) using the **Factory Design Pattern with a registry**. 

## Goals
- Add/remove agent implementations without modifying the factory.
- Register new agent classes automatically.
- Support clean module separation and future extensibility.

---

## Components Overview

| Component     | Role                                                                 |
|---------------|----------------------------------------------------------------------|
| `LLMBaseAgent`| Abstract base class for all LLM agents                              |
| `AGENT_REGISTRY` | Dictionary mapping agent names to classes                         |
| `register_agent(name)` | Decorator to register classes into the registry         |
| `LLMFactory`  | Centralized class to instantiate agents using registered types      |

---

## Checklist for Implementation

### 1. Create a Registry and Abstract Base Class

**File**: `base.py`
```python
from abc import ABC, abstractmethod

AGENT_REGISTRY = {}

def register_agent(name):
    def decorator(cls):
        AGENT_REGISTRY[name.lower()] = cls
        return cls
    return decorator

class LLMBaseAgent(ABC):
    @abstractmethod
    def chat(self, prompt: str) -> str:
        pass

    @abstractmethod
    def cost_per_token(self) -> float:
        pass
```

---

### 2. Create Agent Implementations in Separate Files

**File**: `openai_agent.py`
```python
from base import LLMBaseAgent, register_agent

@register_agent("openai")
class OpenAIAgent(LLMBaseAgent):
    def chat(self, prompt: str) -> str:
        return f"[OpenAI] Response to: {prompt}"

    def cost_per_token(self) -> float:
        return 0.001
```

**File**: `akash_agent.py`
```python
from base import LLMBaseAgent, register_agent

@register_agent("akash")
class AkashAgent(LLMBaseAgent):
    def chat(self, prompt: str) -> str:
        return f"[Akash] You said: {prompt}"

    def cost_per_token(self) -> float:
        return 0.0005
```

---

### 3. Implement the Factory

**File**: `factory.py`
```python
from base import AGENT_REGISTRY

class LLMFactory:
    @staticmethod
    def create_agent(provider: str, **kwargs):
        cls = AGENT_REGISTRY.get(provider.lower())
        if not cls:
            raise ValueError(f"No agent registered for: {provider}")
        return cls(**kwargs)
```

---

### 4. Use in Application Code

**File**: `main.py`
```python
# Ensure agents are imported to register themselves
import openai_agent
import akash_agent
from factory import LLMFactory

agent = LLMFactory.create_agent("openai")
print(agent.chat("Explain Factory pattern."))
```

---

## Recommended Project Layout
```
/llm_agents/
├── base.py
├── factory.py
├── openai_agent.py
├── akash_agent.py
└── __init__.py
```

> Optionally, use `importlib` to scan and import all modules in an `agents/` folder automatically.

---

## Extensions

- [ ] Add metadata per agent (e.g., pricing, model family)
- [ ] Load agents dynamically from config
- [ ] Register agents via plugin discovery (e.g., setuptools entry points)


