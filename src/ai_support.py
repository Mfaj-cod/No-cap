from groq import Groq # type: ignore

from src.config import settings
from src.data import SUPPORT_POLICIES
from src.db import list_products


def _catalog_snapshot() -> str:
    products = list_products()
    if not products:
        return "No products are currently loaded."

    lines = []
    for product in products:
        lines.append(
            (
                f"- {product['name']} | category: {product['category']} | "
                f"retail: Rs. {product['normal_price']:.2f} | "
                f"wholesale at 25+ for shop owners: Rs. {product['shop_owner_price']:.2f}"
            )
        )
    return "\n".join(lines)


def generate_support_response(message: str) -> str:
    if not settings.groq_api_key:
        raise RuntimeError("CapAI is not configured yet. Add GROQ_API_KEY to enable chat.")

    client = Groq(api_key=settings.groq_api_key)

    response = client.chat.completions.create(
        model=settings.groq_model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are the customer care assistant for Nocaps. "
                    "Answer only with the store policies and catalog provided. "
                    "If someone asks for order-specific status, explain that the public assistant "
                    "cannot access private order data and direct them to the account or contact page. "
                    "Keep replies practical, concise, and friendly."
                    f"\n\nPolicies:\n{SUPPORT_POLICIES.strip()}\n\nCatalog:\n{_catalog_snapshot()}"
                ),
            },
            {
                "role": "user",
                "content": f"Customer message:\n{message.strip()}",
            },
        ],
    )

    return response.choices[0].message.content.strip()
