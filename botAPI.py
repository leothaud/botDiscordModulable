import discord, ast, asyncio
import treatMessage

async def async_exec(stmts, env=None):
    parsed_stmts = ast.parse(stmts)

    fn_name = "_async_exec_f"

    fn = f"async def {fn_name}(): pass"
    parsed_fn = ast.parse(fn)

    for node in parsed_stmts.body:
        ast.increment_lineno(node)

    parsed_fn.body[0].body = parsed_stmts.body
    exec(compile(parsed_fn, filename="<ast>", mode="exec"), env)

    return await eval(f"{fn_name}()", env)


async def send(text):   
    n = len(text)//2000
    for i in range(n+1):
        tmp = text[2000*i:2000*(i+1)]
        await treatMessage.currentMessage.channel.send(tmp)
