
var words = ["....", "..."],
    el = document.getElementById('current'),
    word_counter = 0,
    char_counter = 0;

function updateText(){

    el.innerHTML = el.innerHTML + words[word_counter][char_counter++];
    
    if( char_counter == words[word_counter].length ){

        word_counter++; 	
        char_counter = 0;	
        el.innerHTML = '';  
        
        if( word_counter == words.length )
            word_counter = 0;
    }
}
setInterval(updateText,300);