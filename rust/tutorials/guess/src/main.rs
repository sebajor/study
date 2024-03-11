use std::io;
use std::cmp::Ordering;
use rand::Rng;

fn main() {
    
    let secret_number = rand::thread_rng()
            .gen_range(1..=100);

    loop{
        println!("Guess the number");
        let mut guess = String::new();

        io::stdin()
            .read_line(&mut guess)
            .expect("Fail to read input");
        println!("You guess {}",guess);
        //convert the string on the stdio into a integer
        let guess: u32 = match guess.trim().parse() {
            //handle errors
            Ok(num) => num,
            Err(_) => {
                println!("not a number!");
                continue;
                },
            };
        //trim: deletes the whitespaces and \n \r\n
        //parse method make the cast

        match guess.cmp(&secret_number){
            Ordering::Less => println!("Your number is too small"),
            Ordering::Greater => println!("Your number is too big"),
            Ordering::Equal => {
                println!("You win");
                break;
            },
        }
    }
}
