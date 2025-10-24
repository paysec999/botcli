import click
from ai_gemini.main import main_logic

@click.command()
@click.argument('command', type=str, required=False)
@click.option('--options', default='', help='Additional options for the command.')
def cli(command, options):
    """Command-line interface for the AI Gemini bot."""
    if command is None:
        # If no command provided, default to chat interactive mode
        command = 'chat'
    try:
        result = main_logic(command, options)
        click.echo(result)
    except Exception as e:
        click.echo(f"Error: {str(e)}")

if __name__ == '__main__':
    cli()
