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

## OK, what's going on behind the scenes?

The interesting stuff is the macro transformation pass. There is currently only one pass, so if you have an indirectly recursive macro, or a macro that makes another macro, you could be in trouble.

It's not too hard to add another pass though.

### The Macro Transformation Step

1. Compile each macro into a JavaScript function. There are no tricks here. We just pretend that `defmacro` is actually `function` instead.
2. Recurse through the AST and find all calls to macros. 
3. For each macro:
4. Transform arguments from scheme to nested JavaScript lists. (e.g. ["console.log", ["+", 1, 2]]) I'm going to call this data JSON, even though that's technically inaccurate.
5. Run the macro as a JavaScript function with that JSON.
6. The macro will give back new JSON. 
7. Transform that JSON back to scheme.
8. Parse that scheme and replace the current macro call with it.
9. Continue with the parse.

## Design decisions

* `do` - forms like `if` can only take 3 arguments - condition, then-body, else-body - but the bodies may consist of many statements. `do` groups several statements into one.

* I haven't done postfix operators (++, --), and I probably wont. Or maybe I will by just having a rewriter that makes them prefix, and stick it to everyone who uses them in complicated ways.

* `a = (x, y) -> x + y` translates to this:

	`(= a (function (arglist x y) (+ x y)))`

	There are two things to note here. One is "arglist", which is just a list of arguments - I do it this way because just doing `(x y)` would break abstraction (seems like we're calling x with y). 
	The other is that we don't have named functions, just anonymous functions.

* Try catch is a little weird. It takes 4 arguments: try body, catch arglist, catch body, finally body. None of them are optional - you just pass in `(do)` for empty bodies.

## TODO

### High priority

* Write a macro to turn callback soup into something more flat.

### Other stuff

* I should be able to get rid of `brackets`
* Array literal syntax should be tokenized into one big token.
* It is probably possible to replace all semicolons with commas, but I am not sure if this is the case.
* `(gensym)` ? I can hack without it, but maybe I should include it, since otherwise my macros are not technically correct... hmmm.
* Better error messages for macros (grab node traceback at least)
* Tokenizer is currently not smart enough to realize that numbers should be unquoted by default.
* `basic.sc` should be written in coffeescript which is then compiled to sc. derp.
