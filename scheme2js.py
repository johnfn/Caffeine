#!/usr/bin/python
import re
import sys

input = "\n".join([l for l in open(sys.argv[1])])

class Node:
  def __init__(self, name, args):
    assert isinstance(args, list)
    self.name = name
    self.args = args

  def tostr(self, indent):
    indentation = indent * "  "
    result = ""

    result = indentation + self.name
    for arg in self.args:
      result += "\n" + arg.tostr(indent + 1)

    return result

  def __repr__(self):
    return self.tostr(0)

  def wrap(self, str):
    return "(function(){%s;})()" % (str)
  
  def compile(self):
    ops = ["+", "/", "*", "-", "||", "&&", "===", "!==", "!=", "==", "+=", "-=", "/=", "*=", "instanceof", "<", ">", "<=", ">="]
    unary = ["!", "+", "-", "new", "typeof"]

    name = self.name
    if name == "=":
      return "%s = %s" % (self.args[0].compile(), self.args[1].compile())
    elif name == "root":
      return ";\n".join([arg.compile() for arg in self.args])
    elif name == "call":
      return "(%s)()" % self.args[0].compile()
    elif name == "try":
      return "try {\n%s\n} catch %s  {\n%s} finally {\n%s}" % (self.args[0].compile(), self.args[1].compile(), self.args[2].compile(), self.args[3].compile())
    elif name == "do":
      if len(self.args) == 0:
        return self.wrap("return void 0");
      return self.wrap(";\n".join([arg.compile() for arg in self.args[:-1]]) + "\nreturn %s;" % (self.args[-1].compile()))
    elif name == "var":
      return "var %s" % ",".join([arg.compile() for arg in self.args])
    elif name == "root":
      return ";\n".join([arg.compile() for arg in self.args])
    elif name == "==":
      return "%s == %s" % (self.args[0].compile(), self.args[1].compile())
    elif name == "if":
      while len(self.args) < 3:
        self.args.append(Node("void", [Atom("0")])) # Append empty bodies to unfilled parts of the if
      
      return self.wrap("if (%s) {return %s;} else {return %s;}" % (self.args[0].compile(), self.args[1].compile(), self.args[2].compile()))
      # return ("if (%s) {%s;} else {%s;}") % (self.args[0].compile(), self.args[1].compile(), self.args[2].compile())
    elif name == "function":
      return "function %s { %s }" % (self.args[0].compile(), ";".join([arg.compile() for arg in self.args[1:]]))
    elif name == "arglist":
      return "(" + ",".join([arg.compile() for arg in self.args]) + ")"

    for op in ops:
      if name == op and len(self.args) == 2:
        return "(%s %s %s)" % (self.args[0].compile(), op, self.args[1].compile())
    
    for op in unary:
      if name == op and len(self.args) == 1:
        return "(%s %s)" % (op, self.args[0].compile())

    return "%s(%s)" % (self.name, ", ".join([arg.compile() for arg in self.args]))


class Atom:
  def __init__(self, contents):
    self.contents = contents

  def tostr(self, indent):
    return indent * "  " + self.contents

  def compile(self):
    return self.contents
 
  def __repr__(self):
    return "Atom " + self.contents

def is_paren(str):
  return str == "(" or str == ")"

def tokenize(string):
  in_string = False
  string_opener = ""
  tokens = [""]
  for ch in string:
    if ch == "'" or ch == '"':
      in_string = not in_string
      tokens[-1] += ch
      if not in_string: tokens.append("")
      continue

    if not in_string:
      if ch == " ":
        tokens.append("")
        continue

      if is_paren(ch):
        tokens.append(ch)
        tokens.append("")
        continue

    tokens[-1] += ch
      
  tokens = [tok.strip() for tok in tokens[:-1] if tok.strip() != ""]
  return tokens

def parse(string):
  string = string.strip()
  string = "(root " + string + ")"
  tokens = tokenize(string)

  def helper(tokens):
    node_name = tokens[1]
    node_args = [[]]
    tokens = tokens[2:-1] #ignore (, name, and ).

    depth = 0
    for token in tokens:
      if is_paren(token): 
        depth = depth + (1 if token == "(" else -1)
        node_args[-1].append(token)

        if depth == 0: 
          node_args[-1] = helper(node_args[-1])
          node_args.append([])
        continue

      if depth == 0:
        node_args[-1] = Atom(token)
        node_args.append([])
      else:
        node_args[-1].append(token)

    node_args = node_args[:-1]
    return Node(node_name, node_args)
  
  return helper(tokens)

ast = parse(input)

output = sys.argv[1].split(".")[0] + ".js" #same name as input, but .js instead of .sc
open(output, 'w').write(ast.compile())
