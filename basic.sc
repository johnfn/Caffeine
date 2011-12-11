(= util (call require "util"))

(= dump (function (arglist obj)
  (var result)
  (= result (call util.inspect obj false null))
  (if (== (typeof obj) "string")
    (= result (call result.slice 1 (- result.length 1))))
  (call console.log result)))

(= list (function (arglist) 
	(var args)
	(= args (Array.prototype.slice.call arguments))
  (return args)))

(= first (function (arglist list)
  (return ([0] list))))

(= rest (function (arglist list)
  (return (call list.slice 1))))
