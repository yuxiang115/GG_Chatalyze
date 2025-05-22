import asyncio
import json

from app.constant import env_constant
from app.services.open_dota_api_service import fetch_match_details
from app.services import dota_constants_service as dota_constants, llm_analysis_service as llm_analysis
from app.discord_util import discordWebhook as discordWebhook
from app.repository import player_repository
from app.services.open_dota_api_service import fetch_recent_matches
from app.repository.match_repository import MatchRepository

# MongoDB and collections
match_repository = MatchRepository()
matches_collection = match_repository.get_collection("matches")

semaphore = asyncio.Semaphore(env_constant.LLM_MAX_CURRENCY)  # Limit the number of concurrent tasks


processing_set  = set()
processing_lock = asyncio.Lock()
analysis_queue = asyncio.Queue()


def auto_analyze_players_most_recent_matches():
    players_ids = player_repository.fetch_players_id_auto_analyze_enable()
    refresh_matches_by_player_ids(players_ids)


# Function to refresh and fetch new match data
def refresh_matches_by_player_ids(player_ids: list, send_cache_analysis=False):
    recent_match_ids = []
    for player_id in player_ids:
        recent_match_ids += fetch_recent_matches(player_id)

    recent_match_ids = set(recent_match_ids)
    matches_db = match_repository.get_matches(recent_match_ids)
    matches_db = {match["match_id"]: match for match in matches_db}

    result = []

    for match_id in recent_match_ids:
        if match_id in matches_db:
            analysis = matches_db[match_id]["analysis"]
            result.append({'match_detail': dota_constants.fill_match_details(matches_db[match_id]['match_details']), 'analysis': analysis})
            if send_cache_analysis:
                content = [f'### Match ID: {match_id}'] + [message for message in analysis.values()]
                discordWebhook.send(content)
            continue
        match_details = fetch_match_details(match_id)
        if match_details:
            match_detail_original = json.loads(json.dumps(match_details))
            match_details = dota_constants.fill_match_details(match_details)
            print(f"Match details: {json.dumps(match_details)}")
            # analysis = llm_analysis.analyze(match_details)

            run_no_wait(_enqueue_analysis_task(match_id, match_detail_original, match_details))

            result.append({'match_detail': match_details, 'analysis': "Processing..."})
    return result

def analyze_match(match_id, use_cache_analysis=True, send_cache_analysis=False):
    matche_db = match_repository.get_match(match_id)
    if matche_db:
        match_detail = matche_db["match_details"]
        analysis_db = matche_db["analysis"]
        if match_detail and use_cache_analysis:
            content = [f'### Match ID: {match_id}'] + [message for message in analysis_db.values()]
            if send_cache_analysis:
                discordWebhook.send(content)
            return {'match_detail': dota_constants.fill_match_details(match_detail), 'analysis': analysis_db}
    else:
        match_detail = fetch_match_details(match_id)
    if not match_detail:
        return None

    # deep copy the match_detail
    match_detail_original = json.loads(json.dumps(match_detail))
    match_detail = dota_constants.fill_match_details(match_detail)

    run_no_wait(_enqueue_analysis_task(match_id, match_detail_original, match_detail))


    return {'match_detail': match_detail, 'analysis': "Processing..."}


async def _enqueue_analysis_task(match_id, match_detail_original, match_detail_filled):
    should_enqueue = False
    async with processing_lock:
        if match_id not in processing_set:
            processing_set.add(match_id)
            should_enqueue = True

    if should_enqueue:
        await analysis_queue.put((match_id, match_detail_original, match_detail_filled, False))

async def start_analysis_worker():
    while True:
        match_id, match_detail_original, match_detail, savedDB = await analysis_queue.get()
        asyncio.create_task(llm_analysis_task(match_id, match_detail_original, match_detail, savedDB))


async def llm_analysis_task(match_id, match_detail_original, match_detail, savedDB):
    async with semaphore:
        try:
            analysis = await asyncio.to_thread(llm_analysis.analyze, match_detail)
            if not savedDB:
                match_repository.save_match(
                    {"match_details": match_detail_original, "match_id": match_id, "analysis": analysis})
            content = [f'### Match ID: {match_id}'] + [message for message in analysis.values()]
            discordWebhook.send(content)
        except Exception as e:
            print(f"Error analyzing match {match_id}: {e}")
        finally:
            async with processing_lock:
                processing_set.discard(match_id)
            analysis_queue.task_done()



def run_no_wait(coro):
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(coro)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(coro)