from configparser import ConfigParser
from valve.rcon import RCON as rcon
from valve.rcon import RCONCommunicationError, RCONError

import logging
import time
import requests
import click

@click.command()
@click.argument('config', type=click.Path(readable=True))
def main(config):
    c = ConfigParser()
    c.read(config)
    interval = int(c['misc']['sleep'])
    webhook = c['insurgency']['url']
    min_players = int(c['insurgency']['min'])

    # Setup rcon
    server, port = c['insurgency']['server'].split(':')
    port = int(port)
    r = rcon((server, port), c['insurgency']['password'])
    r.connect()
    r.authenticate()
    if not r.authenticated:
        click.secho('Not authenticated!', fg='red')
        raise click.Abort()

    # Logic is simple, check for players, if >=min 'session' starts
    active_session = False
    skipped_cycle = False
    while True:
        if not r.connected:
            click.secho('%d: Waiting %d seconds to reconnect' % (int(time.time()), interval * 2))
            time.sleep(interval * 2)
            r = rcon((server, port), c['insurgency']['password'])
            r.connect()
            r.authenticate()

        try:
            players_line = list(
                filter(lambda x: x.startswith('players'), r('status').splitlines())
            )[0]
            player_count = int(players_line.split(':')[1].strip().split()[0])
        except (RCONCommunicationError, RCONError):
            if skipped_cycle:
                click.secho('%d: RCON error, twice, something is wrong, aborting' % int(time.time()))
                raise click.Abort()
            click.secho('%d: RCON error, map might be changing, skipping this cycle' % int(time.time()))
            skipped_cycle = True
            time.sleep(interval)
            continue
        skipped_cycle = False

        if player_count >= min_players and not active_session:
            click.echo('%d: %d are playing, notifying' % (int(time.time()), player_count))
            active_session = True
            message = 'There\'s %d people playing Insurgency right now, get on mumble if you want in.' % player_count
            b = requests.post(webhook, json={'content': message}, params={'wait': 'true'})
        elif player_count >= min_players and active_session:
            click.echo('%d: Active session, %d playing' % (int(time.time()), player_count))
        else:
            click.echo('%d: %d playing, need %d more' % (int(time.time()), player_count, min_players - player_count))
            active_session = False

        time.sleep(interval)

if __name__ == '__main__':
    main()
