// TODO: pass the list of stop words and offensive words from ParlAI instead of hard-coding them
const STOPWORDS = ['', "\'\'", "\'d", "\'ll", "\'m", "\'re", "\'s", "\'ve", '*',
    ',', '--', '.', '?', '\`\`', 'a', 'about', 'above', 'after',
    'again', 'against', 'ain', 'all', 'also', 'am', 'an', 'and',
    'any', 'are', 'aren', 'as', 'at', 'be', 'because', 'been',
    'before', 'being', 'below', 'between', 'both', 'but', 'by',
    'can', 'couldn', 'd', 'did', 'didn', 'do', 'does', 'doesn',
    'doing', 'don', 'down', 'during', 'each', 'few', 'for', 'from',
    'further', 'had', 'hadn', 'has', 'hasn', 'have', 'haven',
    'having', 'he', 'her', 'here', 'hers', 'herself', 'him',
    'himself', 'his', 'how', 'i', 'if', 'in', 'into', 'is', 'isn',
    'it', 'its', 'itself', 'just', 'know', 'll', 'm', 'ma', 'me',
    'mightn', 'more', 'most', 'mustn', 'my', 'myself', "n't",
    'needn', 'no', 'nor', 'not', 'now', 'o', 'of', 'off', 'on',
    'once', 'only', 'or', 'other', 'our', 'ours', 'ourselves',
    'out', 'over', 'own', 'people', 're', 'really', 's', 'same',
    'see', 'shan', 'she', 'should', 'shouldn', 'so', 'some',
    'such', 't', 'than', 'that', 'the', 'their', 'theirs', 'them',
    'themselves', 'then', 'there', 'these', 'they', 'this',
    'those', 'through', 'to', 'too', 'under', 'until', 'up', 've',
    'very', 'want', 'was', 'wasn', 'we', 'were', 'weren', 'what',
    'when', 'where', 'which', 'while', 'who', 'whom', 'why', 'will',
    'with', 'won', 'wouldn', 'y', 'you', 'your', 'yours',
    'yourself', 'yourselves'];

const OFFENSIVE_WORDS = ['2g1c', '2 girls 1 cup', 'acrotomophilia',
    'alabama hot pocket', 'alaskan pipeline', 'anal',
    'anilingus', 'anus', 'apeshit', 'arsehole', 'ass',
    'asshole', 'assmunch', 'auto erotic', 'autoerotic',
    'babeland', 'baby batter', 'baby juice', 'ball gag',
    'ball gravy', 'ball kicking', 'ball licking', 'ball sack',
    'ball sucking', 'bangbros', 'bareback', 'barely legal',
    'barenaked', 'bastard', 'bastardo', 'bastinado', 'bbw',
    'bdsm', 'beaner', 'beaners', 'beaver cleaver',
    'beaver lips', 'bestiality', 'big black', 'big breasts',
    'big knockers', 'big tits', 'bimbos', 'birdlock', 'bitch',
    'bitches', 'black cock', 'blonde action',
    'blonde on blonde action', 'blowjob', 'blow job',
    'blow your load', 'blue waffle', 'blumpkin', 'bollocks',
    'bondage', 'boner', 'boob', 'boobs', 'booty call',
    'brown showers', 'brunette action', 'bukkake', 'bulldyke',
    'bullet vibe', 'bullshit', 'bung hole', 'bunghole',
    'busty', 'butt', 'buttcheeks', 'butthole', 'camel toe',
    'camgirl', 'camslut', 'camwhore', 'carpet muncher',
    'carpetmuncher', 'chocolate rosebuds', 'circlejerk',
    'cleveland steamer', 'clit', 'clitoris', 'clover clamps',
    'clusterfuck', 'cock', 'cocks', 'coprolagnia', 'coprophilia',
    'cornhole', 'coon', 'coons', 'creampie', 'cum', 'cumming',
    'cunnilingus', 'cunt', 'darkie', 'date rape', 'daterape',
    'deep throat', 'deepthroat', 'dendrophilia', 'dick',
    'dildo', 'dingleberry', 'dingleberries', 'dirty pillows',
    'dirty sanchez', 'doggie style', 'doggiestyle',
    'doggy style', 'doggystyle', 'dog style', 'dolcett',
    'domination', 'dominatrix', 'dommes', 'donkey punch',
    'double dong', 'double penetration', 'dp action',
    'dry hump', 'dvda', 'eat my ass', 'ecchi', 'ejaculation',
    'erotic', 'erotism', 'escort', 'eunuch', 'faggot',
    'fecal', 'felch', 'fellatio', 'feltch', 'female squirting',
    'femdom', 'figging', 'fingerbang', 'fingering', 'fisting',
    'foot fetish', 'footjob', 'frotting', 'fuck', 'fuck buttons',
    'fuckin', 'fucking', 'fucktards', 'fudge packer',
    'fudgepacker', 'futanari', 'gang bang', 'gay sex',
    'genitals', 'giant cock', 'girl on', 'girl on top',
    'girls gone wild', 'goatcx', 'goatse', 'god damn',
    'gokkun', 'golden shower', 'goodpoop', 'goo girl',
    'goregasm', 'grope', 'group sex', 'g-spot', 'guro',
    'hand job', 'handjob', 'hard core', 'hardcore', 'hentai',
    'homoerotic', 'honkey', 'hooker', 'hot carl', 'hot chick',
    'how to kill', 'how to murder', 'huge fat', 'humping',
    'incest', 'intercourse', 'jack off', 'jail bait',
    'jailbait', 'jelly donut', 'jerk off', 'jigaboo',
    'jiggaboo', 'jiggerboo', 'jizz', 'juggs', 'kike',
    'kinbaku', 'kinkster', 'kinky', 'knobbing',
    'leather restraint', 'leather straight jacket',
    'lemon party', 'lolita', 'lovemaking', 'make me come',
    'male squirting', 'masturbate', 'menage a trois', 'milf',
    'missionary position', 'motherfucker', 'mound of venus',
    'mr hands', 'muff diver', 'muffdiving', 'nambla',
    'nawashi', 'negro', 'neonazi', 'nigga', 'nigger',
    'nig nog', 'nimphomania', 'nipple', 'nipples',
    'nsfw images', 'nude', 'nudity', 'nympho',
    'nymphomania', 'octopussy', 'omorashi', 'one cup two girls',
    'one guy one jar', 'orgasm', 'orgy', 'paedophile',
    'paki', 'panties', 'panty', 'pedobear', 'pedophile',
    'pegging', 'penis', 'phone sex', 'piece of shit',
    'pissing', 'piss pig', 'pisspig', 'playboy',
    'pleasure chest', 'pole smoker', 'ponyplay', 'poof',
    'poon', 'poontang', 'punany', 'poop chute', 'poopchute',
    'porn', 'porno', 'pornography', 'prince albert piercing',
    'pthc', 'pubes', 'pussy', 'queaf', 'queef', 'quim',
    'raghead', 'raging boner', 'rape', 'raping', 'rapist',
    'rectum', 'reverse cowgirl', 'rimjob', 'rimming',
    'rosy palm', 'rosy palm and her 5 sisters',
    'rusty trombone', 'sadism', 'santorum', 'scat',
    'schlong', 'scissoring', 'semen', 'sex', 'sexo',
    'sexy', 'shaved beaver', 'shaved pussy', 'shemale',
    'shibari', 'shit', 'shitblimp', 'shitty', 'shota',
    'shrimping', 'skeet', 'slanteye', 'slut', 's&m', 'smut',
    'snatch', 'snowballing', 'sodomize', 'sodomy', 'spic',
    'splooge', 'splooge moose', 'spooge', 'spread legs',
    'spunk', 'strap on', 'strapon', 'strappado', 'strip club',
    'style doggy', 'suck', 'sucks', 'suicide girls',
    'sultry women', 'swastika', 'swinger', 'tainted love',
    'taste my', 'tea bagging', 'threesome', 'throating',
    'tied up', 'tight white', 'tit', 'tits', 'titties',
    'titty', 'tongue in a', 'topless', 'tosser', 'towelhead',
    'tranny', 'tribadism', 'tub girl', 'tubgirl', 'tushy',
    'twat', 'twink', 'twinkie', 'two girls one cup',
    'undressing', 'upskirt', 'urethra play', 'urophilia',
    'vagina', 'venus mound', 'vibrator', 'violet wand',
    'vorarephilia', 'voyeur', 'vulva', 'wank', 'wetback',
    'wet dream', 'white power', 'wrapping men',
    'wrinkled starfish', 'xx', 'xxx', 'yaoi',
    'yellow showers', 'yiffy', 'zoophilia'];

// MIN_TEXT_LENGTH_TO_CHECK_COPY must always be less than OVERLAP_LENGTH_CHECK
// otherwise the check for copy/paste always passes
const MIN_TEXT_LENGTH_TO_CHECK_COPY = 20;
const OVERLAP_LENGTH_CHECK = 30
const MIN_NUM_WORDS_PER_UTTERANCE = 5

function split_tokenize(text) {
    const res = text.replace(/[.|. . .|,|;|:|!|\?|\(|\)]/g, function (x) {
        return ` ${x} `;
    });
    return res.split(" ").filter((w) => w !== "");
}

export default function valid_utterance(text) {
    const lowered_text = text.toLowerCase();
    return !(is_too_short(lowered_text) ||
        has_offensive_words(lowered_text) ||
        has_turker_words(lowered_text))
}

function is_too_short(text) {
    const tokenized_text = split_tokenize(text);
    if (tokenized_text.length < MIN_NUM_WORDS_PER_UTTERANCE) {
        alert("Your message was too short. Please try again and use longer and more engaging messages.");
        return true;
    }
    return false;
}

function has_turker_words(text) {
    if (text.includes("turker") || text.includes("turk")) {
        return !confirm("Please do not mention the mechanical turk task in the conversation." +
            "Press \"Cancel\", to go back and edit, if your message does that, or \"OK\" to send the message.");
    }
    return false
}

function has_offensive_words(text) {
    const tokenized_text = split_tokenize(text);
    const cleaned_text = tokenized_text.filter((w) => STOPWORDS.indexOf(w) === -1);

    // Checking for offensive words
    const offensive_words = cleaned_text.filter((w) => OFFENSIVE_WORDS.indexOf(w) !== -1)
    if (offensive_words.length > 0) {
        const detected_offensive_words = offensive_words.join(', ');
        alert("We have detected the following offensive language in your message: \"" +
            detected_offensive_words +
            "\". Please edit and send again.");
        return true
    }
    return false;
}

