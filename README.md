Twitter changed their API, need a bearer token now.

$ curl --request GET 
    --url 'https://api.twitter.com/1.1/users/show.json?screen_name=twitterdev' 
    --header 'authorization: Bearer <bearer>'
$ curl --request GET 
  --url 'https://api.twitter.com/1.1/users/show.json?screen_name=twitterdev' 
  --header 'authorization: OAuth oauth_consumer_key="consumer-key-for-app", 
  oauth_nonce="generated-nonce", oauth_signature="generated-signature", 
  oauth_signature_method="HMAC-SHA1", oauth_timestamp="generated-timestamp", 
  oauth_version="1.0"'
$ twurl /1.1/users/show.json?screen_name=twitterdev


https://developer.twitter.com/en/docs/accounts-and-users/follow-search-get-users/api-reference/get-users-show
