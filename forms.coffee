sc """
	(= list (function (arglist) 
		(var args)
		(= args (Array.prototype.slice.call arguments))
	  (return args)))

	(= first (function (arglist list)
	  (return ([0] list))))

	(= rest (function (arglist list)
	  (return (call list.slice 1))))
	
	(defmacro varname (arglist somevar)
		(return (list "console.log" (+ "'" somevar "'"))))

  (defmacro myfor (arglist idx start end body)
    (return 
      `(do 
        (while (< ~idx ~end)
          (brackets
            ~body
            (+= ~idx ~1))))))
"""

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

myfor(i, 1, 10, console.log(i + 5))
