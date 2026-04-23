# Ingredient Regex Engine

An NLP engine powered by LLMs for structuring ingredient data.

### 🎯 Objective

Transforms unstructured ingredient lists into a structured data representation.

### 🚀 Core Assumptions

- ingredient name extraction
- quantity and unit identification
- input data normalization
- support for non-standard textual formats

### 🧩 Use Cases

- shopping list processing
- food label analysis
- dietary and meal planning systems
- e-commerce (product data standardization)


---
# ⚙️ Overview

The engine operates in multiple modes.

### 🧠 Learning Mode

The engine accepts a list of ingredients and, using an agent, decomposes each ingredient into components:

- Product name  
- Unit (handful, milliliter, etc.)  
- Unit size (large, small, etc.)  
- Product state (ingredient condition independent of the manufacturer: chopped, cooked, etc.)  

Each component is used to construct a regex pattern that enables data extraction without relying on an LLM and regardless of word inflection.

### ⚡ Structuring Mode

Using the generated regex database, the engine structures data into a `ResolvedIngredient` object

```json
{
  "raw_input": "3 duże garści świeżego szpianku (lub rukoli)",
  "amount": 3.0,
  "unit_size": "duże",
  "unit": "garści",
  "condition": "świeżego",
  "name": "szpianku",
  "extra": "lub rukoli"
}
```

### 🏷️ Categorization Mode

The engine assigns ingredient names from its internal database to appropriate food categories.

### 💾 Persistence Mode

Stores regex registries and categories in a database.  
In the current implementation, the repository is file-based due to the requirement for final human validation of both category assignments and regex parsing.

---

# ⭐ Key Features

### 🤖 Hybrid Approach (LLM + Rules)

### 🧩 Structured Data Extraction from Ingredients

### ⚡ Train Once, Use Without LLM

### 🏗️ Extensible Architecture (Ports & Adapters)

### 🔌 Support for Multiple Input Formats

### 🏷️ Ingredient Categorization

---

# 👉 📌 Examples

## 🏗️ Engine Initialization
### 🔐 Environment Requirements

For proper program execution, setting an API key is required.

Create a `.env` file in the project directory:

```env
OPENAI_API_KEY=your_api_key_here
```

```python
from regex_engine import EngineConfig, AgentConfig, create_engine
from dotenv import load_dotenv

load_dotenv()

default_config = AgentConfig(
  model="gpt-4o-mini",
  timeout=20,
  ensemble_size=5,
  max_retries=3,
)

config = EngineConfig.create(output_dir="path/to/output/directory",
                             parser=AgentConfig(),
                             categorizer=AgentConfig()
                             )

engine = await create_engine(config)
```

- If `and_conjunctions` and `or_conjunctions` are unavailable in the input data or are empty,
  they are initialized automatically during engine bootstrap.
## 🧠 Learning: `learn`

```python

await engine.learn([
    """
    2 duże łyżki ciepłego mleka
    1 szklanka wody
    3 jajka
    5 czubatych łyżek śmietany
    1 i 1/3 słoika dżemu
    """
)
```
### 📦 `RegexRegistry`

#### 🧾 ingredient_name_registry

```json
[
    {
      "stem": "dżem",
      "variants": ["dżem", "dżemami", "dżemem", "dżemu", "dżemy", "dżemów"],
      "pattern": "\\b(?:dżemami|dżemem|dżemów|dżemu|dżemy|dżem)\\b"
    },
    {
      "stem": "jajko",
      "variants": ["jajek", "jajka", "jajkami", "jajkiem", "jajko"],
      "pattern": "\\b(?:jajkami|jajkiem|jajek|jajka|jajko)\\b"
    },
    {
      "stem": "mleko",
      "variants": ["mlek", "mleka", "mlekami", "mlekiem", "mleko"],
      "pattern": "\\b(?:mlekami|mlekiem|mleka|mleko|mlek)\\b"
    },
    {
      "stem": "woda",
      "variants": ["woda", "wodami", "wody", "wodą", "wodę", "wód"],
      "pattern": "\\b(?:wodami|woda|wody|wodą|wodę|wód)\\b"
    },
    {
      "stem": "śmietana",
      "variants": ["śmietan", "śmietana", "śmietanami", "śmietany", "śmietaną", "śmietanę"],
      "pattern": "\\b(?:śmietanami|śmietana|śmietany|śmietaną|śmietanę|śmietan)\\b"
    }
  ]
```

---

#### 📏 unit_registry

```json
[
  {
    "stem": "szklanka",
    "variants": ["szklanek", "szklanka", "szklankami", "szklanki", "szklanką", "szklankę"],
    "pattern": "\\b(?:szklankami|szklanek|szklanka|szklanki|szklanką|szklankę)\\b"
  },
  {
    "stem": "słoik",
    "variants": ["słoik", "słoika", "słoikami", "słoiki", "słoikiem", "słoików"],
    "pattern": "\\b(?:słoikami|słoikiem|słoików|słoika|słoiki|słoik)\\b"
  },
  {
    "stem": "łyżka",
    "variants": ["łyżek", "łyżka", "łyżkami", "łyżki", "łyżką", "łyżkę"],
    "pattern": "\\b(?:łyżkami|łyżek|łyżka|łyżki|łyżką|łyżkę)\\b"
  }
]
```

---

#### 🏷️ unit_size_registry

```json
[
  {
    "stem": "czubaty",
    "variants": ["czubata", "czubate", "czubatego", "czubatej", "czubaty", "czubatych", "czubatym", "czubatymi", "czubatą"],
    "pattern": "\\b(?:czubatego|czubatych|czubatymi|czubatej|czubatym|czubata|czubate|czubaty|czubatą)\\b"
  },
  {
    "stem": "duży",
    "variants": ["duża", "duże", "dużego", "dużej", "duży", "dużych", "dużym", "dużymi", "dużą"],
    "pattern": "\\b(?:dużego|dużych|dużymi|dużej|dużym|duża|duże|duży|dużą)\\b"
  }
]
```

---

#### 🌡️ ingredient_condition_registry

```json
[
  {
    "stem": "ciepły",
    "variants": ["ciepła", "ciepłe", "ciepłego", "ciepłej", "ciepły", "ciepłych", "ciepłym", "ciepłymi", "ciepłą"],
    "pattern": "\\b(?:ciepłego|ciepłych|ciepłymi|ciepłej|ciepłym|ciepła|ciepłe|ciepły|ciepłą)\\b"
  }
]
```

---

#### 🔗 and_conjunctions_registry

```json
[
  {
    "stem": "i",
    "variants": ["i"],
    "pattern": "\\bi\\b"
  },
  {
    "stem": "oraz",
    "variants": ["oraz"],
    "pattern": "\\boraz\\b"
  }
]
```

---

#### 🔗 or_conjunctions_registry

```json
[
  {
    "stem": "albo",
    "variants": ["albo"],
    "pattern": "\\balbo\\b"
  },
  {
    "stem": "bądź",
    "variants": ["bądź"],
    "pattern": "\\bbądź\\b"
  },
  {
    "stem": "ewentualnie",
    "variants": ["ewentualnie"],
    "pattern": "\\bewentualnie\\b"
  },
  {
    "stem": "lub",
    "variants": ["lub"],
    "pattern": "\\blub\\b"
  },
  {
    "stem": "lub_też",
    "variants": ["lub_też"],
    "pattern": "\\blub_też\\b"
  }
]
```

## 🔍`recognize_ingredients`
```python

results = engine.recognize_ingredients([
    "2 słoiki śmietany",                  
    "2 łyżki mleka",                     
    "szklankę ciepłego mleka",             
    "szklanki wody",                     
    "2 jajka",                           
    "czubata łyżka śmietany",            
    "5 łyżek śmietany",                  
    "dżem (lub marmolada)",              
    "słoik dżemu",                       
])
```
```json
[
  {
    "raw_input": "2 słoiki śmietany",
    "amount": 2.0,
    "unit_size": null,
    "unit": "słoik",
    "condition": null,
    "name": "śmietana",
    "extra": ""
  },
  {
    "raw_input": "2 łyżki mleka",
    "amount": 2.0,
    "unit_size": null,
    "unit": "łyżka",
    "condition": null,
    "name": "mleko",
    "extra": ""
  },
  {
    "raw_input": "szklankę ciepłego mleka",
    "amount": 1.0,
    "unit_size": null,
    "unit": "szklanka",
    "condition": "ciepły",
    "name": "mleko",
    "extra": ""
  },
  {
    "raw_input": "szklanki wody",
    "amount": 1.0,
    "unit_size": null,
    "unit": "szklanka",
    "condition": null,
    "name": "woda",
    "extra": ""
  },
  {
    "raw_input": "2 jajka",
    "amount": 2.0,
    "unit_size": null,
    "unit": null,
    "condition": null,
    "name": "jajko",
    "extra": ""
  },
  {
    "raw_input": "czubata łyżka śmietany",
    "amount": 1.0,
    "unit_size": "czubaty",
    "unit": "łyżka",
    "condition": null,
    "name": "śmietana",
    "extra": ""
  },
  {
    "raw_input": "5 łyżek śmietany",
    "amount": 5.0,
    "unit_size": null,
    "unit": "łyżka",
    "condition": null,
    "name": "śmietana",
    "extra": ""
  },
  {
    "raw_input": "dżem (lub marmolada)",
    "amount": 1.0,
    "unit_size": null,
    "unit": null,
    "condition": null,
    "name": "dżem",
    "extra": "lub marmolada"
  },
  {
    "raw_input": "słoik dżemu",
    "amount": 1.0,
    "unit_size": null,
    "unit": "słoik",
    "condition": null,
    "name": "dżem",
    "extra": ""
  }
]
```
##  🗂️ Categorisation
```python
categories = await engine.categorize_registries()
```
```json
{
    "mleko": Category.DAIRY,
    "śmietana": Category.DAIRY,
    "jajko": Category.EGGS,
    "woda": Category.BEVERAGES,
    "dżem": Category.PROCESSED
}
```


---

# 🏗️ Architecture

The system consists of the following components:

- **RegexEngine** – the main system entry point, responsible for orchestrating learning, recognition, and persistence processes.  
- **IngredientLearningEngine** – a component implementing the core learning loop, processing ingredients and initializing regex registry construction.  
- **LearningRules** – a set of rules responsible for filtering and reducing input data during the learning process.  
- **Normalizers (unit, ingredient_name, unit_size, ingredient_condition)** – components responsible for morphological normalization and inflection handling.  
- **IngredientParser** – decomposes an ingredient into semantic components (e.g., name, unit, condition).  
- **RegexRegistry (unit, ingredient_name, unit_size, ingredient_condition, and_conjunctions, or_conjunctions)** – registries storing regex patterns. Each registry is separated into a read (reader) and write (writer) layer.  
- **RegexEntry** – the fundamental registry unit, containing:
  - `stem` (key),  
  - `variants` (word inflections used to construct the regex).  
- **RegexServices (unit, ingredient_name, unit_size, ingredient_condition)** – components responsible for maintaining registry consistency by adding new entries or extending existing ones with additional variants.  
- **RegexOrchestrator** – coordinates services responsible for regex construction and updates.  
- **RegexResolver** – builds a `ResolvedIngredient` object based on data from the RegexRegistry, containing structured fields (`raw_input`, `name`, `amount`, `condition`, `unit`, `unit_size`, `extra`).  
- **InputAdapter** – standardizes input data into the `IngredientRecord` format, regardless of the input source.  
- **Categorizer** – assigns ingredient names to appropriate food categories.  
- **RegexRepository** – responsible for persisting and retrieving regex registries.  
- **CategoryRepository** – responsible for persisting and retrieving ingredient categories.

---

# 🔄 Workflow

The system operates in multiple modes corresponding to successive data processing stages.

## 🧠 `learn(ingredients)`

A function responsible for building the regex database.

### Input

- `str`  
- `list[str]`  
- `pandas`  

Data is converted into the `IngredientRecord` structure.

### 🧹 Initial Filtering

At the beginning, records containing conjunctions are removed,

except when the conjunction occurs:

- between numbers (e.g., "4 and 1/2"),  
- within parentheses.  

### 🔁 Learning Loop

The learning process is iterative:

- Records that can already be structured based on existing regex patterns are removed.  
- The ingredient with the highest occurrence frequency is selected.  
- The ingredient is parsed by the Agent.

**Example:**

`2 duże łyżki ciepłego mleka`

**Parsing result:**

- `2` → amount  
- `duże` → unit_size  
- `łyżki` → unit  
- `ciepłego` → ingredient_condition  
- `mleka` → ingredient_name  

### 🧱 Regex Entry Construction

For each segment:

- if the segment can already be recognized → it is skipped  
- otherwise:
  - a stem is created  
  - existence of a `RegexEntry` is verified  
  - if it exists → a new variant is added  
  - if it does not exist → a new entry is created  

Normalization and inflection handling are based on the Morfeusz library.

---

### 🔤 Normalization

### 🧬 Stem Construction

### `ingredient_name_normalizer`

The phrase is analyzed by `phrase_analyser`, which detects:

- head noun  
- dependent noun  
- adjectives / adjectival participles  
- remaining phrase  

**Example:**

`mąka pszenna typu 2 z nizin himalajskich`

**Analysis:**

- `mąka` → head noun  
- `pszenna` → adjective  
- `typu 2 z nizin himalajskich` → remainder  

**Rules:**

- normalization to nominative singular  
- if two nouns are present → both in nominative  
- for pluralia tantum → plural form


### `adjective_normalizer`

For:

- `unit_size`  
- `ingredient_condition`  

The following form is applied:

- nominative  
- singular  
- masculine gender  

### `unit_normalizer`

Units are normalized to:

- nominative singular  

---

### 🔄 Inflection Generation

After determining the `stem`, inflectional variants are generated.

**Standard set:**

- nominative singular  
- genitive singular  
- accusative singular  
- instrumental singular  
- nominative plural  
- genitive plural  
- instrumental plural  

##### 🧩 Compound Names (Two Nouns)

For names such as:

- `egg yolk`  
- `heavy cream`  

The following combinations are generated:

- both nouns → full inflection set  
- first noun → full inflection set, second → genitive  

##### 🏷️ Adjectives

A standard set is generated for each gender:

- masculine inanimate  
- feminine  
- neuter  

##### 📏 Units

A standard inflection set is generated.
---

### ⚙️ Regex Construction

Based on:

- `stem`  
- `variants`  

the following is created:

`RegexEntry(stem, variants, regex)`

The entry is stored in the appropriate `RegexRegistry`:

- `unit`  
- `unit_size`  
- `ingredient_name`  
- `ingredient_condition`  

---

## 🔍 `recognize_ingredients(ingredients)`

A function responsible for ingredient recognition without using an LLM.

#### ⚡ Flow

- Input data is converted to `IngredientRecord`  
- The system matches fragments against regex patterns from `RegexRegistry`  

##### 🔢 `amount` handling

- if the first token is a number → it is used as `amount`  
- otherwise → `amount = 1`  

If the pattern:

`number + conjunction + number`

→ values are summed  

**Examples:**

`4 and 1/2 cups of water`

**Result:**
```json
{
  "raw_input": "4 i 1/2 szklanki wody",
  "amount": 4.5,
  "unit": "szklanka",
  "unit_size": null,
  "condition": null,
  "name": "woda",
  "extra": ""
}
```

## 🏷️ `categorize_registries()`

- uses the Agent (LLM)  
- assigns ingredients to categories:
  - DAIRY = "nabiał"
  - MEAT = "mięso"
  - FISH_AND_SEAFOOD = "ryby i owoce morza"
  - EGGS = "jajka"
  - GRAINS = "produkty zbożowe"
  - VEGETABLES = "warzywa"
  - FRUITS = "owoce"
  - LEGUMES = "rośliny strączkowe"
  - NUTS_AND_SEEDS = "orzechy i nasiona"
  - FATS_AND_OILS = "tłuszcze i oleje"
  - SUGARS_AND_SWEETENERS = "cukry i słodziki"
  - SPICES_AND_HERBS = "przyprawy i zioła"
  - SAUCES_AND_DRESSINGS = "sosy i dressingi"
  - MUSHROOMS = "grzyby"
  - PROCESSED = "przetworzone"
  - PREPARED_MEALS = "gotowe dania"
  - SOUPS = "zupy/buliony"
  - BEVERAGES = "napoje"
  - ALCOHOL = "alkohol"
  - NON_FOOD = "niejadalne"
  - OTHER = "inne"
  - UNKNOWN = "nieznane"

---

## 💾 `save_registries()`

- saves all `RegexRegistry` instances into separate files  
- if categories are available → data is saved in a grouped form  
---

## 💾 `save_categories()`

Saves:

- `stem`  
- `category`  

---


# 🚀 Quickstart

### Install from GitHub

```bash
pip install git+https://github.com/romanroman008/ingredient_regex_engine.git
```

### Or clone and install locally

```bash
git clone https://github.com/romanroman008/ingredient_regex_engine.git
cd ingredient_regex_engine
pip install .
```

### Optional (faster installs with uv)

```bash
pip install uv
uv pip install git+https://github.com/romanroman008/ingredient_regex_engine.git
```


---

#  🛠️ Tech Stack

- Python 3.11+
- Pydantic v2 (data validation)
- OpenAI Agents SDK (LLM / agent pipeline)
- Morfeusz2 (Polish morphological analysis)
---

# 🤝 Credits

The project utilizes:

- Morfeusz2 – morphological analysis of the Polish language  
- LLM models (OpenAI) – parsing and categorization  

# 📄 License

MIT License