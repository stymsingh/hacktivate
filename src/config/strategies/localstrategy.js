var passport = require('passport'),
    LocalStrategy = require('passport-local').Strategy,
    mongodb = require('mongodb').MongoClient;

module.exports = function() {
    passport.use(new LocalStrategy({
            usernameField: 'email',
            passwordField: 'password'
        },
        function(username, password, done) {
            var url = 'mongodb://duser:duser@ds257838.mlab.com:57838/hhusers';

            mongodb.connect(url, function(err, db) {
                console.log(username);
                var collection = db.collection('users');
                collection.findOne({
                        _id: username
                    },
                    function(err, results) {

                        if (results === null) {
                            return done(null, false, { message: 'Bad user' });
                        }

                        if (results.password === password) {
                            var user = results;
                            done(null, user);
                        } else {
                            done(null, false, { message: 'Bad password' });
                        }




                    }
                );
            });
        }));


};