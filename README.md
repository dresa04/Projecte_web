# League of Legends Django Project

## Descripció del projecte
Aquesta aplicació web permet als usuaris obtenir el **PUUID** (identificador únic de Riot Games) dels jugadors de League of Legends. També proporciona un catàleg de **campions** i **ítems** del joc, amb informació detallada sobre cadascun.

### Funcionalitats principals
- 🔎 **Cerca de PUUID**: Els usuaris poden introduir el seu nom d'invocador i obtenir el seu identificador únic.
- 🏆 **Llista de campions**: Mostra un llistat de tots els campions disponibles amb estadístiques, descripcions i rols.
- 🛡️ **Llista d'ítems**: Permet consultar informació sobre els ítems del joc, incloent-hi el preu i els efectes.

La informació dels campions i els ítems s'obté dels fitxers JSON disponibles a la web de desenvolupadors de Riot Games. La informació per cercar el PUUID es recupera a través de l'API oficial del joc.

---

## Per què és útil aquest projecte?
Aquest projecte és útil per a jugadors de League of Legends i desenvolupadors interessats en integrar informació del joc en les seves pròpies aplicacions. Facilita l'accés ràpid a dades essencials dels jugadors i el catàleg de campions i ítems sense necessitat de consultar fonts externes manualment.

---

## Com començar?
### 📌 Requisits previs
- Python 3.8+
- Django
- Clau d'API de Riot Games (necessària per fer consultes a l'API)

### 🚀 Instal·lació
1. Clona el repositori:
   ```sh
   git clone https://github.com/usuari/repo.git
   cd repo
   ```
2. Crea i activa un entorn virtual:
   ```sh
   python -m venv venv
   source venv/bin/activate  # A Windows: venv\Scripts\activate
   ```
3. Instal·la les dependències:
   ```sh
   pip install -r requirements.txt
   ```
4. Configura les variables d'entorn i afegeix la teva clau d'API de Riot Games.
5. Executa el servidor:
   ```sh
   python manage.py runserver
   ```
6. Accedeix a l'aplicació a `http://127.0.0.1:8000/`

---

## 📞 On rebre ajuda?
Si tens dubtes o problemes amb el projecte, pots:
- Obrir un **Issue** al repositori de GitHub.
- Consultar la documentació de l'API de Riot Games: [https://developer.riotgames.com](https://developer.riotgames.com)
- Contactar amb els mantenidors del projecte.

---

## 👥 Qui manté el projecte?
Aquest projecte és desenvolupat per **Daniel Resa** drp5@alumnes.udl.cat i **Abraham Ruiz** abrahamruizmoste017@gmail.com. Les contribucions són benvingudes! Si vols millorar el projecte, no dubtis a fer un `fork` i enviar una `pull request`.

---

## 📜 Llicència
Aquest projecte es distribueix sota la llicència **MIT**.
