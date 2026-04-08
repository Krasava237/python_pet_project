from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, StyleSheet1, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


ROOT_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = ROOT_DIR.parent
RESULTS_DIR = PROJECT_DIR / "results"


def register_fonts() -> tuple[str, str]:
    fonts_dir = Path("C:/Windows/Fonts")
    regular_path = fonts_dir / "arial.ttf"
    bold_path = fonts_dir / "arialbd.ttf"

    if regular_path.exists() and bold_path.exists():
        pdfmetrics.registerFont(TTFont("PetProjectArial", str(regular_path)))
        pdfmetrics.registerFont(TTFont("PetProjectArialBold", str(bold_path)))
        return "PetProjectArial", "PetProjectArialBold"

    return "Helvetica", "Helvetica-Bold"


def build_styles(regular_font: str, bold_font: str) -> StyleSheet1:
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="ReportTitle",
            parent=styles["Title"],
            fontName=bold_font,
            fontSize=18,
            leading=24,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#17324D"),
            spaceAfter=10,
        )
    )
    styles.add(
        ParagraphStyle(
            name="ReportSubtitle",
            parent=styles["Heading2"],
            fontName=regular_font,
            fontSize=10,
            leading=14,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#4F6478"),
            spaceAfter=14,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SectionHeading",
            parent=styles["Heading2"],
            fontName=bold_font,
            fontSize=13,
            leading=17,
            textColor=colors.HexColor("#17324D"),
            spaceBefore=8,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="BodyRu",
            parent=styles["BodyText"],
            fontName=regular_font,
            fontSize=10.5,
            leading=15,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="BulletRu",
            parent=styles["BodyText"],
            fontName=regular_font,
            fontSize=10,
            leading=14,
            leftIndent=14,
            firstLineIndent=-10,
            bulletIndent=0,
            spaceAfter=4,
        )
    )
    return styles


def bullet(text: str, styles: StyleSheet1) -> Paragraph:
    return Paragraph(f"- {text}", styles["BulletRu"])


def add_section(story: list, styles: StyleSheet1, title: str, items: list[str]) -> None:
    story.append(Paragraph(title, styles["SectionHeading"]))
    for item in items:
        story.append(bullet(item, styles))
    story.append(Spacer(1, 4))


def build_page_number_drawer(font_name: str):
    def page_number_drawer(canvas, doc) -> None:
        canvas.saveState()
        canvas.setFont(font_name, 9)
        canvas.setFillColor(colors.HexColor("#4F6478"))
        canvas.drawRightString(190 * mm, 10 * mm, f"Страница {doc.page}")
        canvas.restoreState()

    return page_number_drawer


LAB_REPORTS = [
    {
        "filename": "lab4_seo_api_report.pdf",
        "title": "Лабораторная работа 4",
        "subtitle": "SEO-оптимизация веб-приложения и интеграция сторонних API",
        "sections": [
            (
                "Что требовалось по заданию",
                [
                    "Добавить SEO-метаданные для публичных страниц, отделить индексируемые маршруты от закрытых и показать семантическую структуру интерфейса.",
                    "Реализовать robots.txt, sitemap.xml, canonical URL, Open Graph, Twitter Card и JSON-LD.",
                    "Подключить внешний API через backend-адаптер с нормализацией ответа и graceful degradation на клиенте.",
                ],
            ),
            (
                "Что доработано по замечаниям",
                [
                    "В frontend/src/shared/seo/Seo.tsx расширен SEO-слой: добавлены keywords, og:site_name, og:locale, og:image:alt, twitter:title, twitter:description, twitter:image и twitter:image:alt.",
                    "В frontend/index.html заменен стандартный favicon на frontend/public/favicon.svg и добавлены fallback meta-теги для keywords и соцсетей.",
                    "В frontend/src/components/AppShell.tsx добавлены семантические landmarks: nav с aria-label, main и footer.",
                    "В frontend/src/pages/PetDetailsPage.tsx хлебные крошки переведены на nav + ol, а публичная карточка оформлена через article/header/section/dl.",
                    "Backend SEO-эндпоинты и служебные заголовки остаются в app/seo.py и app/main.py.",
                ],
            ),
            (
                "Что показать на защите",
                [
                    "frontend/src/shared/seo/Seo.tsx: syncMeta, keywords, Open Graph и Twitter Card.",
                    "frontend/index.html: favicon и fallback meta-теги.",
                    "frontend/src/components/AppShell.tsx: nav, main и footer как пример семантики.",
                    "frontend/src/pages/PetDetailsPage.tsx: breadcrumbs, article и SEO публичной карточки.",
                    "app/seo.py и app/main.py: robots.txt, sitemap.xml и X-Robots-Tag.",
                ],
            ),
            (
                "Локальная проверка",
                [
                    "frontend/src/shared/seo/Seo.test.tsx проверяет canonical, keywords, Open Graph, Twitter Card и JSON-LD.",
                    "frontend/src/pages/PetDetailsPage.test.tsx добавлен как UI-тест на семантические breadcrumbs и article-landmarks.",
                    "npm run test:unit и npm run build в папке frontend проходят успешно.",
                    "python -m pytest -m \"unit or integration\" проходит, включая tests/test_seo_endpoints.py.",
                ],
            ),
        ],
    },
    {
        "filename": "lab5_testing_report.pdf",
        "title": "Лабораторная работа 5",
        "subtitle": "Комплексное тестирование клиентской и серверной частей веб-приложения",
        "sections": [
            (
                "Какие библиотеки используются",
                [
                    "Frontend unit/scenario: Vitest, jsdom, @testing-library/react, @testing-library/jest-dom и @testing-library/user-event.",
                    "Frontend e2e: Playwright (@playwright/test).",
                    "Backend unit/integration: pytest, pytest-asyncio, pytest-cov и FastAPI TestClient.",
                    "Для точечных моков и асинхронных замен используются unittest.mock и AsyncMock внутри backend-тестов.",
                ],
            ),
            (
                "Где это видно в проекте",
                [
                    "Frontend зависимости и скрипты: frontend/package.json.",
                    "Конфигурация unit-тестов и coverage: frontend/vitest.config.ts.",
                    "Конфигурация e2e-контура: frontend/playwright.config.ts и frontend/e2e/app.e2e.ts.",
                    "Backend dev-зависимости: requirements-dev.txt и pytest.ini.",
                    "Backend bootstrap: tests/conftest.py.",
                    "Примеры integration-тестов backend: tests/test_pets_api.py и tests/test_seo_endpoints.py.",
                    "Примеры frontend-тестов: frontend/src/shared/seo/Seo.test.tsx, frontend/src/pages/PetsPage.test.tsx и frontend/src/pages/PetDetailsPage.test.tsx.",
                ],
            ),
            (
                "Что доработано в этой итерации",
                [
                    "Vitest стабилизирован под Windows через pool='threads' и maxWorkers=1 в frontend/vitest.config.ts.",
                    "React warning по react-refresh закрыт выносом AuthContext в frontend/src/app/providers/AuthContext.ts.",
                    "React-hooks warnings закрыты в PetsPage.tsx и PetAttachmentsPanel.tsx.",
                    "Для GitHub Actions добавлен requirements-ci.txt: backend job теперь тянет только тестовый стек без тяжелых ML-зависимостей.",
                ],
            ),
            (
                "Покрытие и результаты",
                [
                    "Frontend unit/scenario: 23 passed, line coverage 73.37%, statements 71.68%, branches 53.58%.",
                    "Backend unit + integration: 16 passed, line coverage по coverage-backend.xml 65.79%, суммарное coverage pytest-cov с branch accounting 61.05%.",
                    "npm run lint проходит без ошибок и без warning.",
                    "python -m ruff check app tests scripts проходит без ошибок.",
                    "Playwright-контур оставлен рабочим, но для живого локального запуска нужен чистый стенд со свободными портами 8001 и 4173.",
                ],
            ),
        ],
    },
    {
        "filename": "lab6_containerization_deploy_report.pdf",
        "title": "Лабораторная работа 6",
        "subtitle": "Контейнеризация и автоматизация развертывания веб-приложения",
        "sections": [
            (
                "Что реализовано локально",
                [
                    "Подготовлены Dockerfile для backend и frontend, docker-compose.yml, .dockerignore и .env.example.",
                    "В docker compose описаны postgres, minio, backend и frontend, а также healthcheck и зависимости между сервисами.",
                    "CI pipeline вынесен в .github/workflows/ci.yml: backend checks, frontend lint/unit/build, e2e и docker build; для backend job используется requirements-ci.txt без тяжелого ML-стека.",
                    "CD pipeline вынесен в .github/workflows/deploy.yml и запускается после успешного CI на main.",
                ],
            ),
            (
                "Что подтверждено проверками",
                [
                    "docker compose config проходит успешно.",
                    "Локально пройдены базовые шаги CI: ruff, pytest, npm run lint, npm run test:unit и npm run build.",
                    "Deploy workflow исправлен так, чтобы при отсутствии DEPLOY_* secrets завершаться статусом Skipped, а не Failure.",
                ],
            ),
            (
                "Фактический статус GitHub Actions на 08.04.2026",
                [
                    "Из-за отсутствия write-доступа к Ilyasir/pet-finder-backend workflow были опубликованы в собственный репозиторий Krasava237/python_pet_project.",
                    "GitHub Actions виден по адресу: https://github.com/Krasava237/python_pet_project/actions",
                    "Для первичного запуска CI был создан и затем автоматически смержен PR: https://github.com/Krasava237/python_pet_project/pull/1",
                    "Deploy run после исправления workflow завершился со статусом Skipped: https://github.com/Krasava237/python_pet_project/actions/runs/24130755043",
                    "На странице Actions видны оба workflow: CI и Deploy; для CI отдельно вынесен test-only backend install, чтобы run не зависел от тяжелых ML-колес.",
                ],
            ),
            (
                "Что показать на защите",
                [
                    ".github/workflows/ci.yml: backend -> frontend -> e2e -> docker, плюс requirements-ci.txt для backend/e2e.",
                    ".github/workflows/deploy.yml: workflow_run, gate по DEPLOY_* secrets и безопасный skip.",
                    "docker-compose.yml: healthcheck, depends_on и опубликованные порты.",
                    "Страницу GitHub Actions с workflow CI и Deploy в репозитории Krasava237/python_pet_project.",
                ],
            ),
        ],
    },
]


def build_report(report: dict, styles: StyleSheet1, page_drawer) -> Path:
    output_path = RESULTS_DIR / report["filename"]
    story = [
        Paragraph(report["title"], styles["ReportTitle"]),
        Paragraph(report["subtitle"], styles["ReportSubtitle"]),
        Spacer(1, 2),
    ]

    for section_title, items in report["sections"]:
        add_section(story, styles, section_title, items)

    document = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=14 * mm,
        title=report["title"],
        author="OpenAI Codex",
    )
    document.build(story, onFirstPage=page_drawer, onLaterPages=page_drawer)
    return output_path


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    regular_font, bold_font = register_fonts()
    styles = build_styles(regular_font, bold_font)
    page_drawer = build_page_number_drawer(regular_font)

    generated = [build_report(report, styles, page_drawer) for report in LAB_REPORTS]
    print("Generated reports:")
    for path in generated:
        print(f"- {path}")


if __name__ == "__main__":
    main()
