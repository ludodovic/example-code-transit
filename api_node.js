var express = require('express');
var router = express.Router();
var http = require('http');
var needle = require("needle");
const Reddit = require('reddit')


const querystring = require('querystring');
const ServerSettings = require('../models/ServerSettings');

router.get('/subreddit', function (req, res, next) {
	var refreshToken = req.user.refreshToken; 


	const parameters = {
		username: req.user.name,
		followed_subs: ["Android"],
		unwanted_subs: []
	}

	needle.post("http://localhost:5000/recommend/subreddits/"+refreshToken, parameters, {json: true}, (err, response, body) => {
		if(err){
			console.log(err);
			res.send([]);
			return;
		}

		if(response.statusCode == 200){
			var toSend = {
				subs: []
			}

			body = JSON.parse(body);
			console.log(body);
			var user_list = body.res_users.join(",");
			var apriori = body.res_apriori.join(",");
			var random = body.res_random.join(",");
			var toget = user_list+","+apriori+","+random;
			
			needle.get("https://www.reddit.com/api/info.json?sr_name="+toget, {json: true}, (errr, ress, bo)=>{
				if(err){
					console.log(err);
					res.send([]);
					return;
				}

				bo.data.children.forEach((sub)=>{
					toSend.subs.push({
						display_name: sub.data.display_name,
						title: sub.data.title.substring(0, 25)+"...",
						description: sub.data.public_description.substring(0, 50)+"...",
						image: sub.data.icon_img,
					});
				});

				res.send(toSend);
			});

		}
		
	});
});

router.post('/sentiment', function (req, res, next) {
	needle.post("http://localhost:5000/analysis/sentiment", {text: req.body.text}, {json: true}, (err, response, body)=>{
		if(err){
			console.log(err);
			res.send();
			return;
		}
		else{
			res.send(JSON.parse(body));
		}
	})
});

router.get('/trending', function (req, res, next) {
	needle.get("http://localhost:5000/trends/get_trends", {json: true}, (err, response, body)=>{
		if(err){
			console.log(err);
			res.send();
			return;
		}
		else{
			res.send(JSON.parse(body));
		}
	})
});

router.post('/chatbot', function (req, res, next) {
	needle.post("http://localhost:5000/chatbot", { text: req.body.text }, { json: true }, (err, response, body) => {
		if (err) {
			console.log(err);
			res.send();
			return;
		}
		else {
			res.send(JSON.parse(body));
		}
	})
});

router.post('/topics/subreddit', function (req, res, next) {
	needle.post("http://localhost:5000/topics/subreddit", { name: req.body.name }, { json: true }, (err, response, body) => {
		if (err) {
			console.log(err);
			res.send();
			return;
		}
		else {
			res.send(JSON.parse(body));
		}
	})
});

router.post('/topics/submission', function (req, res, next) {
	needle.post("http://localhost:5000/topics/submission", { id: req.body.id }, { json: true }, (err, response, body) => {
		if (err) {
			console.log(err);
			res.send();
			return;
		}
		else {
			res.send(JSON.parse(body));
		}
	})
});

router.post('/topics/subreddit_recommendation_from_sub', function (req, res, next) {
	needle.post("http://localhost:5000/topics/subreddit_recommendation_from_sub", { name: req.body.name, top: req.body.top }, { json: true }, (err, response, body) => {
		if (err) {
			console.log(err);
			res.send();
			return;
		}
		else {
			res.send(JSON.parse(body));
		}
	})
});

router.post('/topics/subreddit_recommendation_from_data', function (req, res, next) {
	needle.post("http://localhost:5000/topics/subreddit_recommendation_from_data", { data: req.body.data, top: req.body.top }, { json: true }, (err, response, body) => {
		if (err) {
			console.log(err);
			res.send();
			return;
		}
		else {
			res.send(JSON.parse(body));
		}
	})
});




module.exports = router;
