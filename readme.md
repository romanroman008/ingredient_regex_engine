# Ingredient Regex Engine

Silnik NLP wspierany przez LLM do strukturyzacji danych o składnikach.

### 🎯 Cel

Przekształca nieustrukturyzowane listy składników w uporządkowaną reprezentację danych.

### 🚀 Główne założenia

- ekstrakcja nazw składników
- identyfikacja ilości i jednostek
- normalizacja danych wejściowych
- wsparcie dla niestandardowych formatów tekstowych

### 🧩 Zastosowania

- przetwarzanie list zakupów
- analiza etykiet produktów spożywczych
- systemy dietetyczne i meal-planning
- e-commerce (standaryzacja danych produktowych)


---

# ⚙️ Overview

Silnik posiada parę trybów.

### 🧠 Tryb uczenia się

Silnik przyjmuje listę składników, za pomocą agenta dzieli każdy składnik na części:

- Nazwa produktu  
- Jednostka (garść, mililitr, etc)
- Wielkość jednostki (duża, mały, etc)  
- Stan produktu (stan składnika niezależny od producenta: posiekany, gotowana, etc)  

Z każdej z tych części budowany jest regex, który pozwoli na ekstrakcję danych bez użycia LLM oraz bez względu na fleksję słowa.

### ⚡ Tryb strukturyzacji

Silnik korzystając ze swojej stworzonej bazy regexów strukturyzuje do obiektu `ResolvedIngredient`

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

### 🏷️ Tryb kategoryzacji

Silnik przydziela nazwy składników ze swojej bazy danych do odpowiednich kategorii spożywczych.

### 💾 Tryb zapisu

Zapisuje rejestry regexów oraz kategorie do bazy danych. 
W obecnej implementacji repozytorium bazy danych jest oparte o zapis do pliku, ze względu na konieczną ostateczną weryfikację przez człowieka zarówno kategorii jak i parsowania regexów.


---
# ⭐ Key Features


### 🤖 Hybrydowe podejście (LLM + reguły)

### 🧩 Ekstrakcja ustrukturyzowanych danych ze składników

### ⚡ Uczenie raz, użycie bez LLM

### 🏗️ Rozszerzalna architektura (Ports & Adapters)

### 🔌 Obsługa różnych formatów wejścia

### 🏷️ Kategoryzacja składników


---

# 👉 📌 Przykłady

## 🏗️ Tworzenie silnika
### 🔐 Wymagania środowiskowe

Aby korzystać z funkcji opartych o LLM (np. `learn`, `categorize_registries`), wymagane jest ustawienie klucza API.

Utwórz plik `.env` w katalogu projektu:

```env
OPENAI_API_KEY=your_api_key_here
```

```python
from dataclasses import dataclass
from pathlib import Path

@dataclass
class AgentConfig:
    model: str = "gpt-4o-mini"
    timeout: int = 20
    ensemble_size: int = 5
    max_retries: int = 3


@dataclass
class EngineConfig:
    output_dir: Path
    parser: AgentConfig
    categorizer: AgentConfig
    
config = EngineConfig(
    output_dir=Path("/absolute/path/to/output"),  # pełna ścieżka
    parser=AgentConfig(),
    categorizer=AgentConfig()
)

engine = create_engine(config)
```

- Jeśli `and_conjunctions` oraz `or_conjunctions` nie są dostępne w danych wejściowych lub są puste,
  zostają automatycznie zainicjalizowane podczas bootstrapu silnika.
## 🧠 Uczenie `learn`

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
### 📦 Stan `RegexRegistry` po uczeniu

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

## 🔍 Rozpoznawanie składników `recognize_ingredients`
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
##  🗂️ Kategoryzacja
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

# 🏗️ Architektura

System składa się z następujących komponentów:

- **RegexEngine** – główny punkt wejścia systemu, odpowiedzialny za orkiestrację procesów uczenia, rozpoznawania i zapisu.  
- **IngredientLearningEngine** – komponent realizujący główną pętlę uczenia się systemu, przetwarzający składniki i inicjujący budowę rejestrów regexów.  
- **LearningRules** – zestaw zasad odpowiedzialnych za filtrowanie i redukcję danych wejściowych podczas procesu uczenia.  
- **Normalizers (unit, ingredient_name, unit_size, ingredient_condition)** – komponenty odpowiedzialne za normalizację morfologiczną i obsługę fleksji.  
- **IngredientParser** – rozdziela składnik na komponenty semantyczne (np. nazwa, jednostka, stan).  
- **RegexRegistry (unit, ingredient_name, unit_size, ingredient_condition, and_conjunctions, or_conjunctions)** – rejestry przechowujące wzorce regexów. Każdy rejestr rozdzielony jest na część odczytową (reader) i zapisową (writer).  
- **RegexEntry** – podstawowa jednostka rejestru, zawierająca:
  - `stem` (klucz),  
  - `variants` (odmiany słowa, na podstawie których budowany jest regex).  
- **RegexServices (unit, ingredient_name, unit_size, ingredient_condition)** – komponenty odpowiedzialne za utrzymywanie spójności rejestrów poprzez dodawanie nowych wpisów lub rozszerzanie istniejących o dodatkowe warianty.  
- **RegexOrchestrator** – koordynuje pracę serwisów odpowiedzialnych za budowę i aktualizację regexów.  
- **RegexResolver** – na podstawie danych z RegexRegistry tworzy obiekt `ResolvedIngredient` zawierający ustrukturyzowane dane (`raw_input`, `name`, `amount`, `condition`, `unit`, `unit_size`, `extra`).  
- **InputAdapter** – standaryzuje dane wejściowe do postaci `IngredientRecord`, niezależnie od formatu wejścia.  
- **Categorizer** – przypisuje nazwy składników do odpowiednich kategorii spożywczych.  
- **RegexRepository** – odpowiada za zapis i odczyt rejestrów regexów.  
- **CategoryRepository** – odpowiada za zapis i odczyt kategorii składników.

---

# 🔄 Workflow

System działa w kilku trybach odpowiadających kolejnym etapom przetwarzania danych.

## 🧠 `learn(ingredients)`

Funkcja odpowiedzialna za budowę bazy regexów.

### Wejście

- `str`  
- `list[str]`  
- `pandas`  

Dane są konwertowane do struktury `IngredientRecord`.


### 🧹 Wstępne filtrowanie

Na początku usuwane są rekordy zawierające spójniki:

z wyjątkiem przypadków, gdy spójnik znajduje się:

- pomiędzy liczbami (np. „4 i 1/2”),  
- wewnątrz nawiasów.  

### 🔁 Pętla uczenia

Proces uczenia przebiega iteracyjnie:

- Usuwane są rekordy, które mogą już zostać ustrukturyzowane na podstawie istniejących regexów.  
- Wybierany jest składnik o największej liczbie wystąpień.  
- Składnik poddawany jest parsowaniu przez Agenta.

**Przykład:**

`2 duże łyżki ciepłego mleka`

**Wynik parsowania:**

- `2` → amount  
- `duże` → unit_size  
- `łyżki` → unit  
- `ciepłego` → ingredient_condition  
- `mleka` → ingredient_name  

### 🧱 Budowa wpisów regex

Dla każdego segmentu:

- jeśli segment może zostać już rozpoznany → jest pomijany  
- w przeciwnym przypadku:
  - tworzony jest stem  
  - sprawdzane jest istnienie `RegexEntry`  
  - jeśli istnieje → dodawany jest nowy wariant  
  - jeśli nie istnieje → tworzony jest nowy wpis  

Normalizacja i odmiana oparta jest o bibliotekę Morfeusz.

---

### 🔤 Normalizacja

### 🧬 Tworzenie stem

### `ingredient_name_normalizer`

Fraza analizowana jest przez `phrase_analyser`, który wykrywa:

- rzeczownik nadrzędny  
- rzeczownik podrzędny  
- przymiotniki / imiesłowy przymiotnikowe  
- resztę frazy  

**Przykład:**

`mąka pszenna typu 2 z nizin himalajskich`

**Analiza:**

- `mąka` → rzeczownik nadrzędny  
- `pszenna` → przymiotnik  
- `typu 2 z nizin himalajskich` → reszta  

**Zasady:**

- normalizacja do mianownika liczby pojedynczej  
- jeśli dwa rzeczowniki → oba w mianowniku  
- dla pluralia tantum → liczba mnoga



### `adjective_normalizer`

Dla:

- `unit_size`  
- `ingredient_condition`  

Stosowana forma:

- mianownik  
- liczba pojedyncza  
- rodzaj męski  


### `unit_normalizer`

Jednostki sprowadzane są do:

- mianownika liczby pojedynczej  

---


### 🔄 Generowanie odmian

Po ustaleniu `stem` generowane są warianty fleksyjne.

**Standardowy zestaw:**

- mianownik l.p.  
- dopełniacz l.p.  
- biernik l.p.  
- narzędnik l.p.  
- mianownik l.mn.  
- dopełniacz l.mn.  
- narzędnik l.mn.  

##### 🧩 Nazwy złożone (2 rzeczowniki)

Dla nazw takich jak:

- `żółtko jajka`  
- `śmietanka kremówka`  

Generowane są kombinacje:

- oba rzeczowniki → pełna odmiana  
- pierwszy → pełna odmiana, drugi → dopełniacz  

##### 🏷️ Przymiotniki

Generowane jest standardowego zestaw dla każdego rodzaju:
- męskonieżywotnego  
- żeńskiego  
- nijakiego

##### 📏 Jednostki
Generowany jest standardowy zestaw.

---

### ⚙️ Tworzenie regexów

Na podstawie:

- `stem`  
- `wariantów`  

tworzony jest:

`RegexEntry(stem, variants, regex)`

Wpis zapisywany jest w odpowiednim `RegexRegistry`:

- `unit`  
- `unit_size`  
- `ingredient_name`  
- `ingredient_condition`  

---

## 🔍 `recognize_ingredients(ingredients)`

Funkcja odpowiedzialna za rozpoznawanie składników bez użycia LLM.

#### ⚡ Przebieg

- Dane wejściowe konwertowane są do `IngredientRecord`  
- System dopasowuje fragmenty do regexów z `RegexRegistry`  

##### 🔢 Obsługa `amount`

- jeśli pierwsze słowo jest liczbą → używane jako `amount`  
- jeśli nie → `amount = 1`  

Jeśli wzorzec:

`liczba + spójnik + liczba`

→ wartości są sumowane  


**Przykłady:**

`4 i 1/2 szklanki wody`

**Wynik:**
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

- wykorzystuje Agenta (LLM)  
- przypisuje składniki do kategorii:
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

- zapisuje wszystkie `RegexRegistry` do osobnych plików
- jeśli dostępne są kategorie → zapis pogrupowany
---

## 💾 `save_categories()`

Zapisuje:

- `stem`  
- `category`  

---

## 🚀 Quick Start

---

##  🛠️ Tech Stack

---

## 🤝 Credits

Projekt wykorzystuje:

- Morfeusz2 – analiza morfologiczna języka polskiego
- modele LLM (OpenAI) – parsowanie i kategoryzacja

## 📄 License

MIT License