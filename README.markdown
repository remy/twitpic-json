# TwitPic JSON API

A twitpic JSON API to get your photos back out.

I built this out of frustration with the current Twitpic API, that you can only upload your images. 

This content belongs to us, so we should be able to port it else where if we wish.

## Usage

* http://twitpicapi.appspot.com/rem
* http://twitpicapi.appspot.com/rem?callback=mypics
* http://twitpicapi.appspot.com/rem?callback=mypics&page=2

## Example

<pre><code>[{ 
  id: 'abc',
  url: 'http://s3.amazonaws.com/twitpic/...',
  twitpic_url: 'http://twitpic.com/show/large/abc',
  date: '2009-09-13',
  title: 'My birthday pic'
}]</code></pre>