import grequests
import requests
from config import BASE_SITE, OFFERS_URL, HEADERS, UNIV_API_URL, REGISTRY_SITE, UNIV_DATA_API_URL, OFFERS_UNIVS_URL, OFFERS_LIST_URL, OFFERS_REQUESTS_URL
from console import console, Table, Confirm, Progress
from exceptions import Not200Exception
from collections import OrderedDict


def get_offer_page() -> str:
    """
    Завантажує сторінку конкурсних пропозицій, повертає текст сторінки в випадку успіху.
    Викликає Not200Exception якщо не вдалось отримати доступ
    """
    url = BASE_SITE + OFFERS_URL
    req = requests.get(url, headers=HEADERS)
    if req.ok:
        return req.text
    else:
        raise Not200Exception(req.status_code)


def get_all_univ():
    url = REGISTRY_SITE + UNIV_API_URL
    req = requests.get(url, headers=HEADERS, params={"ut": "1", "exp": "json"}, json=True)
    if req.ok:
        j = req.json()
        if Confirm.ask("Показати таблицю [italic]Закладів Вищої Освіти[/]?", default=False):
            table = Table(title="Universities List")
            table.add_column("#", style="dark_cyan")
            table.add_column("Code", style="cyan")
            table.add_column("Name", style="magenta")
            for index, univ in enumerate(j):
                table.add_row("#" + str(index), univ["university_id"], univ["university_name"])
            console.print(table)
        return j
    else:
        raise Not200Exception(req.status_code)


def get_full_univs_data(univs):
    with Progress() as prog:
        task_get_codes = prog.add_task("Збір кодів університетів", total=len(univs))
        univ_codes = []
        for univ in univs:
            if univ["close_date"] is None:
                code = univ["university_id"]
                univ_codes += [code]
            prog.update(task_get_codes, advance=1)
        task_get_udata = prog.add_task("Збір даних університетів", total=len(univ_codes))
        url = REGISTRY_SITE + UNIV_DATA_API_URL
        rs = (grequests.get(url, params={"id": code, "exp": "json"}, headers=HEADERS) for code in univ_codes)
        udata = []
        for data in grequests.imap(rs):
            if data.ok:
                udata += [data.json()]
            prog.update(task_get_udata, advance=1)
        task_find_facs = prog.add_task("Пошук факультетів університетів", total=len(udata))
        ulist = []
        for u in udata:
            educators = u["educators"]
            if len(educators) > 0:
                name = u["university_name"]
                code = u["university_id"]
                facs = u["facultets"]
                region = u["region_name"]
                shortname = u["university_short_name"]
                shortnames = []
                for f in shortname.split(", "):
                    for s in f.split():
                        shortnames.append(s)
                rs = []
                for ed in educators:
                    rs += [
                        grequests.post(BASE_SITE + OFFERS_UNIVS_URL,
                                       data={"qualification": "1", "education_base": "40",
                                             "speciality": ed["speciality_code"], "region": "",
                                             "university": code, "study_program": "", "education_form": "",
                                             "course": ""}, headers=HEADERS, cookies={"PHPSESSID": "f82eiqbhh9una45imk2s2964df"}, timeout=30)
                    ]
            raw_prop_ids = []
            for unl in grequests.imap(rs):
                if unl.ok:
                    json_data = unl.json()
                    try:
                        universities = json_data["universities"]
                    except KeyError:
                        universities = []
                    if len(universities) > 0:
                        ids = universities[0]["ids"]
                        if len(ids) > 0:
                            raw_prop_ids += [ids]
            prop_ids = list(OrderedDict.fromkeys(raw_prop_ids))
            all_prop_ids = []
            if len(prop_ids) > 0:
                for prop_id in prop_ids:
                    prid = prop_id.split(",")
                    all_prop_ids += prid
            if len(all_prop_ids) > 0:
                # з допомогою реквестів зробити запит з айдішками, витягнути звідти всі потрібні дані, зібрати разом, добавити в список, вернути список, і придумати щось для запису в БД
                all_ids = ",".join(all_prop_ids)
                r = requests.post(BASE_SITE + OFFERS_LIST_URL, data={"ids": all_ids}, headers=HEADERS)
                if r.ok:
                    jdata = r.json()
                    offers = jdata.get("offers", [])
                    specs = []
                    for offer in offers:
                        contest_subjects = []
                        for o in offer["os"]:
                            oso = offer["os"][o]
                            contest_subject = {
                                "name": oso["sn"],  # Назва предмету
                                "type": oso["t"],  # Тип
                                "koef": oso["k"],  # Коефіцієнт
                                "minim": oso.get("mv", "Не вказано")  # Мінімальний бал
                            }
                            contest_subjects += [contest_subject]
                        try:
                            stc = offer["st"]["c"]
                            stat = {
                                "statm_all_count": stc["t"],  # Подано заяв
                                "statm_admitted": stc["a"],  # Допущено до конкурсу
                                "statm_budget": stc["b"],  # Заяв на бюджет
                                "mark_avg": stc["ka"],  # Середній бал
                                "mark_max": stc["kx"],  # Максимальний бал
                                "mark_min": stc["km"],  # Мінімальний бал
                            }
                        except KeyError:
                            stat = {
                                "unspecified": True
                            }
                        usid = offer.get("usid", "Не вказано")
                        rq = requests.post(BASE_SITE + OFFERS_REQUESTS_URL, data={"id": usid, "last": 0}, headers=HEADERS)
                        if rq.ok:
                            ja = rq.json()
                            reqs = []
                            rqs = ja.get("requests", "Не вказно")
                            for i in rqs:
                                if isinstance(i, dict):
                                    ii = {
                                        "pib": i.get("fio", "Не вказано"),  # ПІБ
                                        "priority": i.get("p", "Не вказано"),  # Пріоритет
                                        "rss": i.get("rss", "Не вказано"),  # Дані про оцінки
                                        "kv": i.get("kv", "Не вказано"),  # Невідомо
                                        "n": i.get("n", "Не вказано")  # n
                                    }
                                    reqs += [ii]
                        else:
                            reqs = "Не вказано"
                        spec = {  # Спеціальність
                            "spec_code": offer.get("ssc", "Не вказано"),  # Код спеціальності
                            "spec_name": offer.get("ssn", "Не вказано"),  # Назва спеціальності
                            "fac_name": offer.get("ufn", "Не вказано"),  # Факультет
                            "prop_name": offer.get("usn", "Не вказано"),  # Назва пропозиції
                            "prop_type": offer.get("ustn", "Не вказано"),  # Тип пропозиції
                            "study_program": offer.get("spn", "Не вказано"),  # Освітня програма
                            "licenses_count": offer.get("ol", "Не вказано"),  # Ліцензійний обсяг
                            "max_gov_order_count": offer.get("ox", int(offer.get("ol", "0")) - int(offer.get("oc", offer.get("ol", "0")))),  # Максимальний обсяг держзамовлення
                            "contract_count": offer.get("oc", "Не вказано"),  # Обсяг на контракт
                            "contest_subjects": contest_subjects,  # Конкурсні предмети
                            "stat": stat,  # Статистика заяв
                            "rqs": reqs  # Список вступників
                        }
                        specs += [spec]
                    u = {
                        "name": name,  # Назва університету
                        "short_name": shortnames,  # Скорочення назви
                        "code": code,  # Код університету
                        "region": region,  # Область
                        "facs": facs,  # Список факультетів
                        "specs": specs  # Список спеціальностей
                    }
                    ulist += [u]
            prog.update(task_find_facs, advance=1)
    return ulist
