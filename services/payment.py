import stripe
import os
from dotenv import load_dotenv

load_dotenv()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

def create_checkout_session():
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            'price_data': {
                'currency': 'inr',
                'product_data': {'name': 'FinanceGPT Pro Access'},
                'unit_amount': 49900,  
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url="http://localhost:8501?payment=success",
        cancel_url="http://localhost:8501?payment=cancel",
    )
    return session.url
