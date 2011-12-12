sc """
	(= list (function (arglist) 
		(var args)
		(= args (Array.prototype.slice.call arguments))
	  (return args)))

	(= first (function (arglist list)
	  (return ([0] list))))

	(= rest (function (arglist list)
	  (return (list.slice 1))))
  
  (= map (function (arglist func coll)
    (var result idx)
    (= result [])
    (= idx 0)
    (while (!= result.length coll.length)
      (brackets
        (result.push (func ([] coll idx)))
        (+= idx 1)))
    (return result)))
	
	(defmacro varname (arglist somevar)
		(return (list "console.log" (+ '"' somevar '"'))))

  (defmacro myfor (arglist idx start end body)
    (return 
      `(do 
        (while (< ~idx ~end)
          (brackets
            ~body
            (+= ~idx ~1))))))

  (= cons (function (arglist head tail)
    (return (head.concat tail))))
  
  (defmacro turnintolist (arglist body)
    (return
      (cons (list "list") (rest body))))

  (defmacro whenlet (arglist somevar cond body)
    (return 
      `(if ~cond
          (do
            (= ~somevar ~cond)
            ~body))))

  (= islist (function (arglist obj)
    (return (instanceof obj Array))))

  (= die (function (arglist body)
    (console.log "Constraint failed at " body)))
  
  (defmacro constrain (arglist somevar cond body)
    (if (! (islist body)) 
      (return body)
      (if (== (first body) "=")
        (return (list "do" body
                   (list "if" cond (list "die" (+ '"(' (body.join " ") ')"')))))
        (return (map (function (arglist x) (return (constrain somevar cond x))) body)))))
"""
###
###

###
  (defmacro myfor (arglist idx start end body)
    (return 
      (list "do"
        (list "while" (list "<" idx end)
          (list "brackets"
            body
            (list "+=" idx 1))))))
###

###
  (defmacro comp (arglist mylist fn)
    (return
      (list "do"
        (var i)
        (= i 0)
        (list "while" (list "<" i mylist.length)
          (list "brackets"
###

i = 0

(constrain(v, v > 5, ->
  v = 6
  v = 5
  v = 4
  false
))()

myfor(i, 1, 10, console.log(i + 5))
whenlet(i, 5, console.log(i))
console.log(turnintolist(thisisnonexistent(1,2,3,4)))
