var express = require('express');
var app = express();
var port = 5000;
var mongodb = require('mongodb').MongoClient;
request = require('request');

app.listen(port, function(err) {
    console.log('system running on Port: ', port);
});


var cookieParser = require('cookie-parser');
var bodyParser = require('body-parser');
var passport = require('passport');
var session = require('express-session');
app.use(cookieParser());
app.use(session({
    secret: 'hashhacks',
    resave: false,
    saveUninitialized: false

}));

app.use(express.static('public'));
require('./src/config/passport')(app);
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));
app.set('views', './src/views');
app.set('view engine', 'ejs');

var userrouter = express.Router();
var authRouter = express.Router();

app.get('/signup', function(req, res) {
    res.set('Cache-Control', 'no-cache, private, no-store, must-revalidate, max-stale=0, post-check=0, pre-check=0');
    res.render('sign-up');
})

app.get('/login', function(req, res) {

    res.set('Cache-Control', 'no-cache, private, no-store, must-revalidate, max-stale=0, post-check=0, pre-check=0');
    res.render('login');
})

app.get('/', function(req, res) {
    res.render('frontpage');
});

app.use('/auth', authRouter);

app.use('/user', userrouter);

authRouter.route('/signin')
    .post(passport.authenticate('local', {
        failureRedirect: '/login'
    }), function(req, res) {
        res.set('Cache-Control', 'no-cache, private, no-store, must-revalidate, max-stale=0, post-check=0, pre-check=0');
        res.redirect('/user/dashboard');
    });

//
var unirest = require('unirest');
authRouter.route('/register')
    .post(function(req, res) {
        var url =
            'mongodb://duser:duser@ds257838.mlab.com:57838/hhusers';
        mongodb.connect(url, function(err, db) {
            var collection = db.collection('users');
            var user = {
                _id: req.body.email,
                password: req.body.password,
                name: req.body.name,
                address: req.body.add,
                city: req.body.city,
                state: req.body.state,
                zip: req.body.zip,
                hash: ' '
            };
            collection.findOne({
                _id: user._id
            }, function(err, results) {
                if (results === null) {
                    console.log('im in');

                    unirest.get("http://localhost:8000/add/?timestamp=0217240&email=aryan@gmail.com&lat=0.94&long=20.2&energy=50&unit=5")
                        .send()
                        .end(response => {
                            if (response.ok) {
                                user.hash = response.body.hash;
                                collection.insert(user, function(err, results) {


                                    req.login(results.ops[0], function() {
                                        res.redirect('/user/dashboard');

                                    });
                                });
                                console.log(user);
                                console.log("Got a response: ", response.body.hash)
                            } else {
                                console.log("Got an error: ", response.error)
                            }
                        });

                } else {
                    res.redirect('/login');

                }
            })

        });
    });

authRouter.use(function(req, res, next) {
    if (!req.user) {
        return res.redirect('/login');
    }
    res.set('Cache-Control', 'no-cache, private, no-store, must-revalidate, max-stale=0, post-check=0, pre-check=0');
    next();
});

userrouter.use(function(req, res, next) {
    if (!req.user) {
        return res.redirect('/login');
    }
    res.set('Cache-Control', 'no-cache, private, no-store, must-revalidate, max-stale=0, post-check=0, pre-check=0');
    next();
});

userrouter.route('/dashboard')
    .get(function(req, res) {

        res.render('bs', {
            id: req.user._id,
            hash: req.user.hash

        });
    });


userrouter.route('/sell')
    .get(function(req, res) {

        res.render('bs', {
            id: req.user._id

        });
    });


app.get('/logout', function(req, res) {
    req.logout();
    res.redirect('/login');
});