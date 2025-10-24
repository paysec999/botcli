import click
from ai_gemini.main import main_logic

@click.command()
@click.argument('args', nargs=-1)
def cli(args):
    """Command-line interface for the AI Gemini bot."""
    if not args:
        command = 'chat'
        options = ''
    else:
        command = args[0]
        options = ' '.join(args[1:])
    try:
        result = main_logic(command, options)
        click.echo(result)
    except Exception as e:
        click.echo(f"Error: {str(e)}")

if __name__ == '__main__':
    cli()
