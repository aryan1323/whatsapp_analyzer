from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import io, base64, re
import numpy as np
from datetime import timedelta


app = Flask(__name__)
CORS(app)  # allow all origins


global_df = None  # store parsed chat


def fig_to_base64():
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()
    return encoded


@app.route('/analyze', methods=['POST'])
def analyze_chat():
    global global_df
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'No file uploaded'}), 400
    msg = file.read().decode('utf-8')

    pattern = re.compile(r"\[(.*?)\] (.*?): (.*)")
    data = []
    for line in msg.split("\n"):
        match = pattern.match(line)
        if match:
            date_time, sender, message = match.groups()
            date_str, time_str = date_time.split(",", 1)
            date_obj = pd.to_datetime(date_str.strip(), format="%d/%m/%y").date()
            time_obj = pd.to_datetime(time_str.strip(), format="%I:%M:%S %p").time()
            data.append([date_obj, time_obj, sender, message])

    df = pd.DataFrame(data, columns=["Date", "Time", "Sender", "Message"])
    df['Date'] = pd.to_datetime(df['Date'])
    df['year'] = df['Date'].dt.year
    df['month'] = df['Date'].dt.month_name()
    df['day'] = df['Date'].dt.day
    df['Time'] = pd.to_datetime(df['Time'].astype(str))
    df['hour'] = df['Time'].dt.hour
    df['minute'] = df['Time'].dt.minute
    df['dayofweek'] = df['Date'].dt.day_name()
    df['msg_len'] = df['Message'].str.len()

    global_df = df
    users = sorted(df['Sender'].unique().tolist())
    return jsonify({'users': users})


@app.route('/stats', methods=['GET'])
def stats():
    global global_df
    if global_df is None:
        return jsonify({'error': 'Upload a chat first'}), 400

    sender = request.args.get('sender', '')
    if sender:
        df_user = global_df[global_df['Sender'] == sender]
        label = sender
    else:
        df_user = global_df
        label = 'All Users'

    plt.style.use('seaborn-v0_8')
    plt.rcParams.update({'font.size': 12})

    charts = []

    # 0: Messages per Day
    daily_counts = df_user.groupby('Date').size()
    plt.figure(figsize=(14,6))
    daily_counts.plot(color='navy')
    plt.title(f'📅 Messages per Day - {label}')
    plt.xlabel('Date'); plt.ylabel('Messages'); plt.grid(alpha=0.3)
    charts.append({'id': '0', 'title':'Messages per Day', 'img':'data:image/png;base64,' + fig_to_base64()})

    # 1: Messages per Month
    monthly_counts = df_user.groupby(['year','month']).size().reset_index(name='count')
    plt.figure(figsize=(14,6))
    plt.bar(monthly_counts['month'], monthly_counts['count'], color='teal')
    plt.title(f'📆 Messages per Month - {label}')
    plt.xlabel('Month'); plt.ylabel('Messages'); plt.xticks(rotation=45, ha='right')
    charts.append({'id': '1', 'title':'Messages per Month', 'img':'data:image/png;base64,' + fig_to_base64()})

    # 2: Messages by Hour
    hourly_counts = df_user.groupby('hour').size()
    plt.figure(figsize=(12,5))
    hourly_counts.plot(kind='bar', color='orange')
    plt.title(f'⏰ Messages by Hour - {label}')
    plt.xlabel('Hour of Day (0–23)'); plt.ylabel('Messages'); plt.xticks(rotation=0)
    charts.append({'id': '2', 'title':'Messages by Hour', 'img':'data:image/png;base64,' + fig_to_base64()})

    # 3: Messages by Day of Week
    dow_counts = df_user.groupby('dayofweek').size().reindex(
        ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'])
    plt.figure(figsize=(10,5))
    dow_counts.plot(kind='bar', color='skyblue', edgecolor='black')
    plt.title(f'📊 Messages by Day of Week - {label}')
    plt.xlabel('Day'); plt.ylabel('Messages'); plt.xticks(rotation=45, ha='right')
    charts.append({'id': '3', 'title':'Messages by Day of Week', 'img':'data:image/png;base64,' + fig_to_base64()})

    # 4: Pie - Share of Messages by Sender (only if all users)
    if not sender:
        sender_counts = df_user['Sender'].value_counts()
        plt.figure(figsize=(8,8))
        sender_counts.plot(kind='pie', autopct='%1.1f%%', startangle=90, colors=sns.color_palette('pastel'))
        plt.title('💬 Share of Messages by Sender')
        plt.ylabel('')
        charts.append({'id': '4', 'title':'Share of Messages', 'img':'data:image/png;base64,' + fig_to_base64()})

    # 5: Word Cloud
    text = ' '.join(df_user['Message'].dropna())
    if text.strip():
        wc = WordCloud(width=1000, height=500, background_color='white', colormap='tab10').generate(text)
        plt.figure(figsize=(15,7))
        plt.imshow(wc, interpolation='bilinear')
        plt.axis('off')
        plt.title(f'☁️ Most Common Words - {label}', fontsize=16)
        charts.append({'id': '5', 'title':'Word Cloud', 'img':'data:image/png;base64,' + fig_to_base64()})

    # 6: Activity Heatmap (Day vs Hour)
    heatmap_data = df_user.groupby([df_user['dayofweek'], 'hour']).size().unstack(fill_value=0).reindex(
        ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'])
    plt.figure(figsize=(14,6))
    sns.heatmap(heatmap_data, cmap='Blues', linewidths=0.5)
    plt.title(f'🔥 Activity Heatmap (Day vs Hour) - {label}')
    plt.xlabel('Hour of Day'); plt.ylabel('Day of Week')
    charts.append({'id': '6', 'title':'Heatmap', 'img':'data:image/png;base64,' + fig_to_base64()})

    # 7: Message Length Distribution
    plt.figure(figsize=(12,6))
    sns.histplot(df_user['msg_len'].dropna(), bins=30, color='purple')
    plt.title(f'✍️ Message Length Distribution - {label}')
    plt.xlabel('Message Length (characters)')
    plt.ylabel('Count')
    charts.append({'id': '7', 'title':'Message Length Distribution', 'img':'data:image/png;base64,' + fig_to_base64()})

    # 8: Top Active Users Over Time (If all users)
    if not sender:
        plt.figure(figsize=(14,7))
        top_users = df_user['Sender'].value_counts().nlargest(5).index
        for user in top_users:
            user_daily = df_user[df_user['Sender'] == user].groupby('Date').size()
            user_daily.cumsum().plot(label=user)
        plt.title('👥 Top 5 Users Activity Over Time')
        plt.xlabel('Date'); plt.ylabel('Cumulative Messages'); plt.legend()
        charts.append({'id': '8', 'title':'Top 5 Users Activity Over Time', 'img':'data:image/png;base64,' + fig_to_base64()})

    # 9: Emoji Usage Frequency
    emoji_pattern = re.compile(
        "[" 
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "]+", flags=re.UNICODE)
    all_emojis = []
    for msg in df_user['Message'].dropna():
        all_emojis.extend(emoji_pattern.findall(msg))
    if all_emojis:
        emoji_counts = pd.Series(all_emojis).value_counts().nlargest(15)
        plt.figure(figsize=(12,6))
        emoji_counts.plot(kind='bar', color='gold')
        plt.title(f'😀 Top Emoji Usage - {label}')
        plt.xlabel('Emoji'); plt.ylabel('Count')
        charts.append({'id': '9', 'title':'Top Emoji Usage', 'img':'data:image/png;base64,' + fig_to_base64()})

    # 10: Average Response Time Distribution (minutes)
    df_user_sorted = df_user.sort_values(['Date', 'Time'])
    df_user_sorted['datetime'] = pd.to_datetime(df_user_sorted['Date'].dt.strftime('%Y-%m-%d') + ' ' + df_user_sorted['Time'].dt.strftime('%H:%M:%S'))
    df_user_sorted['response_time'] = df_user_sorted['datetime'].diff().dt.total_seconds().div(60).fillna(0)
    rt_filtered = df_user_sorted[(df_user_sorted['response_time'] > 0) & (df_user_sorted['response_time'] < 1440)]
    if not rt_filtered.empty:
        plt.figure(figsize=(12,6))
        sns.histplot(rt_filtered['response_time'], bins=50, color='coral')
        plt.title(f'⏳ Message Response Time Distribution (minutes) - {label}')
        plt.xlabel('Response Time (minutes)'); plt.ylabel('Count')
        charts.append({'id': '10', 'title':'Response Time Distribution', 'img':'data:image/png;base64,' + fig_to_base64()})

    # 11: Daily Active Users (DAU) - only for all users
    if not sender:
        dau = df_user.groupby('Date')['Sender'].nunique()
        plt.figure(figsize=(14,6))
        dau.plot(color='green')
        plt.title('📅 Daily Active Users (DAU)')
        plt.xlabel('Date'); plt.ylabel('Unique Active Users')
        charts.append({'id': '11', 'title':'Daily Active Users (DAU)', 'img':'data:image/png;base64,' + fig_to_base64()})

    # 12: Conversation Starter Frequency (messages following 1+hr inactivity)
    df_user_sorted['time_diff'] = df_user_sorted['datetime'].diff().fillna(pd.Timedelta(seconds=0))
    conversation_starts = df_user_sorted[df_user_sorted['time_diff'] > pd.Timedelta(hours=1)]
    cs_counts = conversation_starts['Sender'].value_counts()
    if not cs_counts.empty:
        plt.figure(figsize=(10,6))
        cs_counts.plot(kind='bar', color='purple')
        plt.title(f'🔑 Conversation Starters - {label}')
        plt.xlabel('User'); plt.ylabel('Count of Conversation Starts')
        charts.append({'id': '12', 'title':'Conversation Starters', 'img':'data:image/png;base64,' + fig_to_base64()})

    # 13: Media Messages Count
    media_indicators = ['<Media omitted>', 'http://', 'https://']
    def is_media(msg):
        msg = str(msg)
        return any(ind in msg for ind in media_indicators)
    media_msgs = df_user[df_user['Message'].apply(is_media)]
    media_counts = media_msgs['Sender'].value_counts()
    if not media_counts.empty:
        plt.figure(figsize=(10,6))
        media_counts.plot(kind='bar', color='teal')
        plt.title(f'📷 Media Messages Count - {label}')
        plt.xlabel('User'); plt.ylabel('Number of Media Messages')
        charts.append({'id': '13', 'title':'Media Messages Count', 'img':'data:image/png;base64,' + fig_to_base64()})

    total_days = df_user['Date'].dt.date.nunique()
    total_messages = len(df_user)
    total_words = df_user['Message'].dropna().str.split().apply(len).sum()

    stats = {
        'sender': label,
        'total_days': int(total_days),
        'total_messages': int(total_messages),
        'total_words': int(total_words)
    }

    return jsonify({'stats': stats, 'charts': charts})

@app.route('/summary', methods=['GET'])
def summary():
    global global_df
    if global_df is None:
        return jsonify({'error': 'Upload a chat first'}), 400

    start_str = request.args.get('start')
    end_str = request.args.get('end')

    if not start_str or not end_str:
        return jsonify({'error': 'Please provide start and end dates'}), 400

    try:
        start_date = pd.to_datetime(start_str).normalize()
        end_date = pd.to_datetime(end_str).normalize()
    except Exception:
        return jsonify({'error': 'Invalid date format'}), 400

    end_plus_one = end_date + pd.Timedelta(days=1)

    df_filtered = global_df[(global_df['Date'] >= start_date) & (global_df['Date'] < end_plus_one)]

    if df_filtered.empty:
        return jsonify({'error': 'No messages found in the given date range'}), 404

    total_messages = len(df_filtered)
    top_sender_counts = df_filtered['Sender'].value_counts()
    top_sender = top_sender_counts.idxmax() if not top_sender_counts.empty else None
    top_sender_count = int(top_sender_counts.max()) if not top_sender_counts.empty else 0

    most_active_hour_counts = df_filtered['hour'].value_counts()
    most_active_hour = int(most_active_hour_counts.idxmax()) if not most_active_hour_counts.empty else None

    # Top 10 most common words (basic cleaning to remove stopwords)
    words_series = df_filtered['Message'].dropna().str.lower().str.findall(r'\b\w+\b')
    all_words = pd.Series([word for sublist in words_series for word in sublist])
    stopwords = set([
        'a', 'an', 'the', 'and', 'or', 'but', 'if', 'to', 'for', 'of', 'in', 'on',
        'is', 'it', 'this', 'that', 'with', 'as', 'at', 'by', 'from', 'you', 'i',
        'he', 'she', 'they', 'we', 'me', 'my', 'our', 'your', 'so', 'do', 'don',
        'just', 'not', 'was', 'are', 'have', 'has', 'had', 'be', 'will', 'can'
    ])
    filtered_words = all_words[~all_words.isin(stopwords)]
    top_words_counts = filtered_words.value_counts().head(10)
    top_words = top_words_counts.index.tolist()

    summary_data = {
        'total_messages': int(total_messages),
        'top_sender': top_sender,
        'top_sender_count': top_sender_count,
        'most_active_hour': most_active_hour,
        'top_words': top_words,
    }

    return jsonify(summary_data)

if __name__ == '__main__':
    app.run(debug=True)
