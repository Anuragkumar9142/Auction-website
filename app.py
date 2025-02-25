from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Model for the Auction Items
class Auction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(300), nullable=False)
    starting_price = db.Column(db.Float, nullable=False)
    current_bid = db.Column(db.Float, nullable=False, default=0.0)

# Model for Bids
class Bid(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    auction_id = db.Column(db.Integer, db.ForeignKey('auction.id'), nullable=False)
    bid_amount = db.Column(db.Float, nullable=False)
    auction = db.relationship('Auction', backref=db.backref('bids', lazy=True))

# Create the database
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    auctions = Auction.query.all()
    return render_template('index.html', auctions=auctions)

@app.route('/auction/<int:id>', methods=['GET', 'POST'])
def auction(id):
    auction = Auction.query.get(id)
    if request.method == 'POST':
        bid_amount = float(request.form['bid_amount'])
        if bid_amount > auction.current_bid:
            auction.current_bid = bid_amount
            new_bid = Bid(auction_id=id, bid_amount=bid_amount)
            db.session.add(new_bid)
            db.session.commit()
        else:
            return "Bid must be higher than the current bid."
    return render_template('auction.html', auction=auction)

@app.route('/create', methods=['GET', 'POST'])
def create_auction():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        starting_price = float(request.form['starting_price'])
        auction = Auction(title=title, description=description, starting_price=starting_price, current_bid=starting_price)
        db.session.add(auction)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('create_auction.html')

if __name__ == "__main__":
    app.run(debug=True)
