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
                    "В frontend/index.html заменен стандартный vite favicon на проектный frontend/public/favicon.svg и добавлены fallback meta-теги для description, keywords и соцсетей.",
                    "В frontend/src/components/AppShell.tsx добавлены семантические landmarks: nav с aria-label, main и footer.",
                    "В frontend/src/pages/PetDetailsPage.tsx хлебные крошки переведены на nav + ol, а карточка объявления сохранена как article/header/section/dl.",
                    "Backend SEO-эндпоинты остаются в app/seo.py, а заголовок X-Robots-Tag и подключение sitemap/robots реализованы в app/main.py.",
                ],
            ),
            (
                "Что показать на защите",
                [
                    "frontend/src/shared/seo/Seo.tsx: функции syncMeta и блок meta-тегов, где выставляются keywords, Open Graph и Twitter Card.",
                    "frontend/index.html: favicon и базовые fallback meta-теги.",
                    "frontend/src/components/AppShell.tsx: nav, main и footer как пример семантики верхнего уровня.",
                    "frontend/src/pages/PetDetailsPage.tsx: семантические хлебные крошки, article и SEO для публичной карточки питомца.",
                    "app/seo.py и app/main.py: robots.txt, sitemap.xml и X-Robots-Tag для служебных маршрутов.",
                ],
            ),
            (
                "Локальная проверка",
                [
                    "frontend/src/shared/seo/Seo.test.tsx обновлен и проверяет canonical, keywords, Open Graph, Twitter Card и JSON-LD.",
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
                    "Для точечных моков и асинхронных замен используются стандартные unittest.mock и AsyncMock внутри backend-тестов.",
                ],
            ),
            (
                "Где это видно в проекте",
                [
                    "Frontend зависимости и скрипты: frontend/package.json.",
                    "Конфигурация frontend unit-тестов и coverage: frontend/vitest.config.ts.",
                    "Конфигурация e2e-контура: frontend/playwright.config.ts и frontend/e2e/app.e2e.ts.",
                    "Backend dev-зависимости: requirements-dev.txt и pytest.ini.",
                    "Backend test bootstrap: tests/conftest.py.",
                    "Примеры integration-тестов backend: tests/test_pets_api.py и tests/test_seo_endpoints.py.",
                    "Примеры frontend-тестов: frontend/src/shared/seo/Seo.test.tsx, frontend/src/pages/PetsPage.test.tsx, frontend/src/pages/PetDetailsPage.test.tsx.",
                ],
            ),
            (
                "Что доработано в этой итерации",
                [
                    "Vitest стабилизирован под Windows через pool='threads' и maxWorkers=1 в frontend/vitest.config.ts, поэтому npm run test:unit теперь запускается без ручных флагов.",
                    "React warning по react-refresh закрыт выносом AuthContext в отдельный файл frontend/src/app/providers/AuthContext.ts.",
                    "React-hooks warnings закрыты в PetsPage.tsx и PetAttachmentsPanel.tsx без ослабления логики приложения.",
                ],
            ),
            (
                "Покрытие и результаты",
                [
                    "Frontend unit/scenario: 23 passed, line coverage 73.37%, statements 71.68%, branches 53.58%.",
                    "Backend unit + integration: 16 passed, line coverage по coverage-backend.xml 66.53%, суммарное coverage pytest-cov с branch accounting 61.64%.",
                    "npm run lint проходит без ошибок и без warning.",
                    "python -m ruff check app tests scripts проходит без ошибок.",
                    "Playwright-контур оставлен рабочим, но для живого запуска нужен чистый стенд со свободными портами 8001 и 4173.",
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
                    "CI pipeline вынесен в .github/workflows/ci.yml: backend checks, frontend lint/unit/build, e2e и docker build.",
                    "CD pipeline вынесен в .github/workflows/deploy.yml и запускается только после успешного CI на main.",
                ],
            ),
            (
                "Что подтверждено проверками",
                [
                    "docker compose config проходит успешно.",
                    "Локально пройдены те же базовые шаги, что используются в CI: ruff, pytest, npm run lint, npm run test:unit и npm run build.",
                    "Deploy workflow настроен корректно на skip без DEPLOY_HOST, DEPLOY_USER, DEPLOY_SSH_KEY, DEPLOY_TARGET_DIR и DEPLOY_ENV_FILE.",
                ],
            ),
            (
                "Честный статус GitHub Actions на 08.04.2026",
                [
                    "Файлы workflow уже есть в локальном проекте: .github/workflows/ci.yml и .github/workflows/deploy.yml.",
                    "На удаленном main этих workflow пока нет, поэтому на странице GitHub Actions еще нельзя увидеть реальные run history по этому проекту.",
                    "После публикации branch или PR станет виден workflow CI, а deploy появится только после попадания workflow в main и успешного CI.",
                    "В отчете специально не указываются вымышленные URL запусков: сначала нужен push на GitHub, потом можно приложить ссылки на конкретные runs.",
                ],
            ),
            (
                "Что показать на защите",
                [
                    ".github/workflows/ci.yml: последовательность backend -> frontend -> e2e -> docker.",
                    ".github/workflows/deploy.yml: условия workflow_run и проверка DEPLOY_* secrets.",
                    "docker-compose.yml: healthcheck, depends_on и опубликованные порты.",
                    "Frontend nginx и backend health endpoints как основу для smoke check после деплоя.",
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
