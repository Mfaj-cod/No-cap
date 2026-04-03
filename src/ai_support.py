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
        raise RuntimeError("Customer Care AI is not configured yet. Add GROQ_API_KEY to enable chat.")

    try:
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_groq import ChatGroq
    except ImportError as exc:
        raise RuntimeError(
            "LangChain Groq dependencies are missing. Install the updated requirements first."
        ) from exc

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                (
                    "You are the customer care assistant for Apna Swad Caps. "
                    "Answer only with the store policies and catalog provided. "
                    "If someone asks for order-specific status, explain that the public assistant "
                    "cannot access private order data and direct them to the account or contact page. "
                    "Keep replies practical, concise, and friendly."
                ),
            ),
            (
                "human",
                "Policies:\n{policies}\n\nCatalog:\n{catalog}\n\nCustomer message:\n{message}",
            ),
        ]
    )

    chain = prompt | ChatGroq(model=settings.groq_model, api_key=settings.groq_api_key) | StrOutputParser()
    return chain.invoke(
        {
            "policies": SUPPORT_POLICIES.strip(),
            "catalog": _catalog_snapshot(),
            "message": message.strip(),
        }
    ).strip()
