from flask import Flask, render_template, request, jsonify
import openai, stripe, os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

@app.route('/')
def index():
    return render_template('index.html', stripe_key=os.getenv("STRIPE_PUBLIC_KEY"))

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    name = data['name']
    category = data['category']
    features = data['features']

    prompt = f"""
    You are a professional e-commerce copywriter. Write a compelling, SEO-optimized product description for:

    Product Name: {name}
    Category: {category}
    Key Features: {features}

    Tone: Friendly, benefit-driven, and conversion-focused. Limit to 150 words.
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    description = response['choices'][0]['message']['content']
    return jsonify({'description': description.strip()})

@app.route('/checkout', methods=['POST'])
def checkout():
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': 'AI Description Credits',
                },
                'unit_amount': 500,
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url='http://localhost:5000',
        cancel_url='http://localhost:5000',
    )
    return jsonify({'id': session.id})

if __name__ == '__main__':
    app.run(debug=True)