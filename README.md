# Caffeine

## CoffeeScript -> "Scheme" -> JavaScript

Compiles CoffeeScript to an intermediary Scheme-like language, which is then translated to JavaScript.

## Usage

`./caff myfile`. Note: NOT `./caff myfile.coffee`! 

Will generate myfile.sc, the intermediate "scheme" code.

## How are macros introduced
		
Given `while`, which executes the body until the condition is true, we introduce `for` like so:

	(defmacro for (arglist varname start end body)
		`(= (unquote varname) start)
		`(while (! (== (unquote varname) end))
			(+= (unquote varname) 1)
			body))

The macro is not a function but is instead a specification of how to transform the syntax in a preliminary pass.o

Ideally, if you're coding in CoffeeScript, you would write something like this:

		for(i, 1, 10, console.log(i))

That syntax would get translated to this scheme:

		(for i 1 10 (console.log i))

Then the macro pass would translate that into this scheme:

		(= i 1)
		(while (! (== i 10))
			(+= i 1)
			(console.log i))


## Design decisions

* `do` - forms like `if` can only take 3 arguments - condition, then-body, else-body - but the bodies may consist of many statements. `do` groups several statements into one.

* I haven't done postfix operators (++, --), and I probably wont. Or maybe I will by just having a rewriter that makes them prefix, and stick it to everyone who uses them in complicated ways.

* `a = (x, y) -> x + y` translates to this:

	`(= a (function (arglist x y) (+ x y)))`

	There are two things to note here. One is "arglist", which is just a list of arguments - I do it this way because just doing `(x y)` would break abstraction (seems like we're calling x with y). 
	The other is that we don't have named functions, just anonymous functions.

* Try catch is a little weird. It takes 4 arguments: try body, catch arglist, catch body, finally body. None of them are optional - you just pass in `(do)` for empty bodies.

## TODO

* I should be able to get rid of `brackets`
* I should get rid of call, too.
* Array literal syntax should be tokenized into one big token.
* It is probably possible to replace all semicolons with commas, but I am not sure if this is the case.
