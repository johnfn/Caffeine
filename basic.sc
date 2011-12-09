(= list (function (arglist) 
	(var args)
	(= args (Array.prototype.slice.call arguments))
  (return args)))

(= first (function (arglist list)
  (return ([0] list))))

(= rest (function (arglist list)
  (return (call list.slice 1))))
